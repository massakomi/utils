import re

from flask import Flask, render_template, request

from init import loadUrl
from test import getLinks

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def seo():  # put application's code here
    post = {
        'urlLinks': 'https://nginx.org/ru/docs/beginners_guide.html',
        'urlTest': 'https://nginx.org/ru/docs/beginners_guide.html',
        'seoTest': 'https://nginx.org/ru/docs/beginners_guide.html',
    }
    for key, value in post.items():
        if request.form.get(key):
            post[key] = request.form.get(key)

    url = request.form.get('urlLinks')
    if url:
        content = loadUrl(url)
        links = getLinks(content, url)

    return render_template('seo.html', **post)

@app.route('/urllinks', methods=['GET', 'POST'])
def urllinks():
    url = 'https://nginx.org/ru/docs/beginners_guide.html'

    content = loadUrl(url)

    return [1, 2]



if __name__ == '__main__':
    app.run()
