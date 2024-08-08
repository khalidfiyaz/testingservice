from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import subprocess
import os

app = Flask(__name__)

# Get the microservice URL from environment variable or use a default
MICROSERVICE_URL = os.getenv('MICROSERVICE_URL', 'http://default-microservice-url')

@app.route('/')
def home():
    return redirect(url_for('test_form'))

@app.route('/startTest', methods=['POST'])
def start_test():
    test_type = request.form['test_type']
    script_mapping = {
        'network_delay': 'network_delays.js',
        'resource_exhaustion': 'exhaustion.js',
        'trigger_bugs': 'bugs.js',
        'sample_test': 'test2.js'
    }
    script_path = os.path.join(os.path.dirname(__file__), script_mapping[test_type])
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            env = os.environ.copy()
            env['MICROSERVICE_URL'] = MICROSERVICE_URL
            process = subprocess.Popen(['k6', 'run', script_path],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       env=env)
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                test_results = stdout.decode() + stderr.decode()
                return render_template_string('''
                    <!doctype html>
                    <html lang="en">
                    <head>
                        <title>Test Results</title>
                        <style>
                            pre {white-space: pre-wrap; word-wrap: break-word;}
                        </style>
                    </head>
                    <body>
                        <h1>Test Results</h1>
                        <pre>{{ results }}</pre>
                        <a href="/">Back to Test Form</a>
                    </body>
                    </html>
                ''', results=test_results)
            else:
                retries += 1
        except Exception as e:
            retries += 1
            continue

    return jsonify({"error": "Failed to start test after {} retries.".format(max_retries)}), 500

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
