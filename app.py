from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    # handle the form data and interact with the test bed
    data = request.form
    print(data)  # process and validate the data here
    return render_template('result.html', message='Configuration submitted successfully!')

if __name__ == '__main__':
    app.run(debug=True)
