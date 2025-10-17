import csv
import os

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    params = {
        'content': '',
        'csv': 'utils/data/technotorg.csv'
    }
    if request.method == 'POST':
        params['content'] = f'calling...'
        params['csv'] = request.form.get('csv')

        if os.path.exists(params['csv']):
            header = None
            data = []
            with open(params['csv'], "r", newline="") as file:
                reader = csv.reader(file, delimiter=';', quotechar='|')
                for row in reader:
                    if header is None:
                        header = row
                    else:
                        values = dict(zip(header, row))
                        data.append(values)
            print(data)
        else:
            params['content'] = f'file not found: {params["csv"]}'

    return render_template('seo-meta-checker.html', **params)

if __name__ == '__main__':
    app.run()
