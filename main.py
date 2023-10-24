import requests
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/parsing.html')
def parsing():
    return render_template('parsing.html')


@app.route('/sqlite.html', methods=['POST', 'GET'])
def sqlite():
    return render_template('sqlite.html')


if __name__ == '__main__':
    app.run(debug=True)