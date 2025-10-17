from collections import defaultdict

from flask import Flask, render_template, request

from utils.init import loadUrl, getLinks, loadUrlEx

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        output = f'calling...'
        if request.form['submit'] == 'get-links':
            output = getLinksProcess()
        if request.form['submit'] == 'analise-url':
            output = analiseUrl()
        return output
    return render_template('seo-links-check.html')

def getLinksProcess():
    link = request.form['url']
    content = loadUrl(link)
    links = getLinks(content, link)
    output = f" content={str(len(content))} links ({str(len(links))}):<br />"
    output += "<br />".join(links)
    return output

def analiseUrl():
    link = request.form['url']
    content = loadUrl(link)
    stat = analiseLinks(content, link)
    return f'<p>Stat: {[f'{key}: {value}' for key, value in stat.items()]} </p>'

def analiseLinks(content, link, level=0):
    stat = defaultdict(int)
    stat ['test'] = 1
    links = getLinks(content, link)
    for url in links:
        data = loadUrlEx(url)
        if not data:
            stat ['Ошибка запроса'] += 1
            continue
        content, status, location, contentType = data
        stat ['Всего загружено ссылок'] += 1
        stat[f'Статус {status}'] += 1
        if content == '':
            stat['Пустой контент'] += 1
        if level > 1:
            continue
        subLinks = getLinks(content, url)
        if len(subLinks) == 0:
            continue
    return stat

if __name__ == '__main__':
    app.run()
