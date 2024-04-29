from flask import Flask, jsonify, request, render_template_string
import subprocess
import os  

app = Flask(__name__)

# Assuming results are stored here
test_results = None

@app.route('/')
def home():
    return "Welcome to the Test Bed API!", 200

@app.route('/startTest', methods=['POST'])
def start_test():
    global test_results
    script_path = os.path.join(os.path.dirname(__file__), 'test.js')
    try:
        process = subprocess.Popen(
            ['k6', 'run', script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        test_results = stdout.decode() + stderr.decode()
        return jsonify({"status": "Test completed successfully", "output": "Results are available."}), 200
    except Exception as e:
        return jsonify({"error": "Failed to start test: " + str(e)}), 500

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

@app.route('/testform', methods=['GET'])
def test_form():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <title>Test Controls</title>
    </head>
    <body>
        <h1>Test Bed Controls</h1>
        <h2>Start Test</h2>
        <form action="/startTest" method="post">
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
