from flask import Flask, jsonify, request, render_template_string, redirect, url_for
import subprocess
import os  

app = Flask(__name__)

# Store the latest test results here
test_results = None

@app.route('/')
def home():
    return redirect(url_for('test_form'))

@app.route('/startTest', methods=['POST'])
def start_test():
    global test_results
    microservice_url = request.form['microservice_url']
    test_type = request.form['test_type']
    
    # Mapping test types to their respective k6 script files
    script_mapping = {
        'network_delay': 'network_delays.js',
        'resource_exhaustion': 'exhaustion.js',
        'trigger_bugs': 'bugs.js',
        'sample_test': 'test2.js'
    }
    
    script_path = os.path.join(os.path.dirname(__file__), script_mapping[test_type])
    max_retries = 3  # Maximum number of retries for a test
    retries = 0
    last_error = None  # Variable to store the last error encountered

    while retries < max_retries:
        try:
            # Set up the environment variable for the k6 script
            env = os.environ.copy()
            env['MICROSERVICE_URL'] = microservice_url

            # Run the k6 script with the dynamically set URL
            process = subprocess.Popen(
                ['k6', 'run', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            stdout, stderr = process.communicate()
            if process.returncode == 0:
                test_results = stdout.decode() + stderr.decode()
                return jsonify({"status": "Test completed successfully", "output": "Results are available."}), 200
            else:
                last_error = f"Test failed with exit code {process.returncode}: {stderr.decode()}"
                retries += 1
        except Exception as e:
            last_error = str(e)
            retries += 1

    return jsonify({"error": f"Failed to start test after {max_retries} retries: {last_error}"}), 500

@app.route('/testResults', methods=['GET'])
def get_test_results():
    if test_results is not None:
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
                <a href="/testform">Back to Test Form</a>
            </body>
            </html>
        ''', results=test_results)
    else:
        return jsonify({"error": "No test results available"}), 404

@app.route('/testform', methods=['GET', 'POST'])
def test_form():
    if request.method == 'POST':
        return redirect(url_for('start_test'))
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Test Controls</title>
    </head>
    <body>
        <h1>Test Bed Controls</h1>
        <form action="/startTest" method="post">
            <label for="microservice_url">Microservice URL:</label>
            <input type="text" id="microservice_url" name="microservice_url" value="http://172.20.10.2:8000" required>
            <br><br>
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
        <h2>View Results</h2>
        <form action="/testResults" method="get">
            <button type="submit">View Results</button>
        </form>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
