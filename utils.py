import csv
import os

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    params = {
        'content': ''
    }
    if request.method == 'POST':
        pass

    return render_template('utils.html', **params)

if __name__ == '__main__':
    app.run()
