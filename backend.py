import os
import subprocess
from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import logging
import psycopg2
import json

app = Flask(__name__)

# Get the microservice URL and Grafana URL from environment variables or use defaults
MICROSERVICE_URL = os.getenv('MICROSERVICE_URL', 'http://cloned_microservice:5001')
GRAFANA_URL = os.getenv('GRAFANA_URL', 'http://localhost:3000/d/dduyazd8n7rwgc/dashboard-test-results?orgId=1')

@app.route('/')
def home():
    return redirect(url_for('test_form'))

# Set up basic logging
logging.basicConfig(level=logging.INFO)

@app.route('/startTest', methods=['POST'])
def start_test():
    test_type = request.form['test_type']
    script_mapping = {
        'network_delay': 'network_delays.js',
        'resource_exhaustion': 'exhaustion.js',
        'trigger_bugs': 'bugs.js',
        'sample_test': 'test2.js'
    }

    if test_type not in script_mapping:
        return jsonify({"error": "Invalid test type selected."}), 400

    script_path = os.path.join(os.path.dirname(__file__), script_mapping[test_type])
    if not os.path.isfile(script_path):
        return jsonify({"error": f"Test script not found: {script_path}"}), 500

    env = os.environ.copy()

    process = subprocess.Popen(
        ['k6', 'run', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env
    )
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        logging.info('Test executed successfully, now attempting to write to PostgreSQL.')

        try:
            connection = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'postgres'),
                database=os.getenv('POSTGRES_DB', 'mydb'),
                user=os.getenv('POSTGRES_USER', 'myuser'),
                password=os.getenv('POSTGRES_PASSWORD', 'passwordgroup50')
            )
            cursor = connection.cursor()

            # Insert into test_results table
            cursor.execute("INSERT INTO test_results (result, details) VALUES (%s, %s) RETURNING id",
                           ("Test success", "results added to table"))
            test_id = cursor.fetchone()[0]
            connection.commit()

            # Parse detailed results and insert into detailed_test_results table
            detailed_results = parse_k6_output(stdout.decode('utf-8'))
            logging.info(f'Parsed detailed results: {detailed_results}')

            for detail in detailed_results:
                cursor.execute("INSERT INTO detailed_test_results (test_id, metric, value) VALUES (%s, %s, %s)",
                               (test_id, detail['metric'], detail['value']))
            
            connection.commit()
            cursor.close()
            connection.close()
            logging.info('Data successfully written to PostgreSQL.')

        except Exception as e:
            logging.error(f'Error writing to PostgreSQL: {str(e)}')

        return render_template_string('''
            <!doctype html>
            <html lang="en">
            <head>
                <title>Test Results</title>
            </head>
            <body>
                <h1>Test Started Successfully</h1>
                <p>Check Grafana for test results.</p>
                <p><a href="{{ grafana_url }}" target="_blank">View Results on Grafana</a></p>
                <a href="/">Back to Test Form</a>
            </body>
            </html>
        ''', grafana_url=GRAFANA_URL)
    else:
        return jsonify({"error": "Test failed to start. Error: " + stderr.decode()}), 500

@app.route('/testform', methods=['GET', 'POST'])
def test_form():
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <title>Test Controls</title>
        </head>
        <body>
            <h1>Test Bed Controls</h1>
            <form action="/startTest" method="post">
                <label for="test_type">Choose a test to perform:</label>
                <select name="test_type" id="test_type">
                    <option value="network_delay">Network Delay</option>
                    <option value="resource_exhaustion">Resource Exhaustion</option>
                    <option value="trigger_bugs">Trigger Bugs</option>
                    <option value="sample_test">Sample Test</option>
                </select>
                <br><br>
                <button type="submit">Start Test</button>
            </form>
        </body>
        </html>
    ''')

def parse_k6_output(output):
    detailed_results = []
    lines = output.splitlines()
    for line in lines:
        try:
            parts = line.split()
            metric = parts[0]
            value = float(parts[1])
            detailed_results.append({'metric': metric, 'value': value})
        except (IndexError, ValueError) as e:
            logging.error(f"Error parsing line: {line} - {str(e)}")
            continue
    return detailed_results

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
