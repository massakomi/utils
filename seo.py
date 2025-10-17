import os
import re
from collections import defaultdict
from urllib.parse import urlparse

from flask import Flask, render_template, request

from init import loadUrl, getLinks, curlLoad, loadUrlEx, w3cErrors, getMetas
from utils.init import extension

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
    url = request.form.get('urllinks')
    content = curlLoad(url)
    links = getLinks(content, url)
    return links

@app.route('/urltest', methods=['GET', 'POST'])
def urltest():
    url = request.form.get('urltest')
    content, status, location, contentType = curlLoad(url, ext=True)
    add = ''
    if location:
        add = f'Редирект: <a href="{location}">{location}</a> '
    return f"""
    <div><b>Тест урла</b> <a href="{url}" target="_blank">{url}</a> 
    <br />Контент: {len(content)}  Статус: <b>{status}</b>
    {add}
    </div>
    """

def ht(url):
    add = after = ''
    data = loadUrlEx(url)
    status = 'empty'
    if data:
        content, status, location, contentType = data
        if location:
            add = ' title="location: ' + location + '"'
            content, status2, location2, contentType = loadUrlEx(location)
            after  = ' --> <a href="' + location + '" title="' + location2 + '">' + status2 + '</a>'
    return '<a href="' + url + '"' + add + '>' + status + '</a>' + after

@app.route('/seotest', methods=['GET', 'POST'])
def seotest():
    site = request.form.get('seotest')
    ext = extension(site)
    if not ext and not site.endswith('/'):
        site += '/'

    a = urlparse(site)
    scheme = 'https' if not a.scheme else a.scheme

    if not a.hostname:
        host = site.replace('/', '')
        site = f'https://{site}/'
    else:
        host = a.hostname

    host = host.replace('www.', '')
    hostWWW = 'www.' + host

    output = ""

    # 1 Проверка дубля www
    output += f'www проверка: {ht(scheme + '://' + host)} '
    output += f' / {ht(scheme + '://' + hostWWW)} <br />'

    # 2 Проверка 404
    output += f' 404 проверка: {ht(site + 'not-exist-url')} <br />'

    # 3 index php
    output += f'index.php проверка: {ht(site)} / {ht(scheme + '://' + host + '/index.php')}<br />'

    # 4 Слэш проверка
    base = os.path.dirname(site)
    output += f' слэш проверка: {ht(base)} / {ht(base + '/')}<br />'

    # 5 Валидация
    url, error = w3cErrors(site)
    output += f' <a href="{url}">W3C валидация</a> - {error}<br />'

    # 6 Ссылки
    limit = 40
    content = loadUrl(site)
    links = getLinks(content, site)
    #print(f'url={site}, fn={loadUrl.fileName}, content = {len(content)} links = {len(links)}')
    links = links[0:limit]
    stat = defaultdict(int)
    titles = defaultdict(str)
    output += f'<h3>Анализ ссылок и контента (<a href="{site}">url</a>, total {len(links)}, limit {limit})</h3>'
    for url in links:
        link = urlparse(url)
        data = loadUrlEx(url)
        if not data:
            raise Exception(f'Empty data {url}')
        content, status, location, contentType = data
        if contentType == 'text/xml':
            continue
        length = str(len(content))
        stat ['links'] += 1

        output += f' <a href="{url}">{link.path}</a> - <b>{status}</b> <span style="color:green">{contentType}</span> ' + length
        if location:
            output += f' <a href="{location}" target="_blank">{location}</a> '
        if length:
            res = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
            title = res[1] if res else ''
            titles [url] = title
        res = re.search(r'(<meta name="keywords" content="(.*?)")', content, re.I | re.S)
        if res:
            stat['keywords'] += 1
            if res[1]:
                stat['keywordsFilled'] += 1
        res = re.search(r'(<meta name="description" content="(.*?)")', content, re.I | re.S)
        if res:
            stat['description'] += 1
            if res[1]:
                stat['descriptionFilled'] += 1
        output += '<br />'

    output += f'<p>Stat: {[f'{key}: {value}' for key, value in stat.items()]} </p>'

    output += '<h3>Найденные титлы</h3>'
    for k, v in titles.items():
        output += '<div><a href="' + k + '">' + v + '</a></div>'

    return f"""
    {output}
    """


def startScanAjax(domain):
    a = urlparse(domain)
    content = loadUrl(domain, cache=False)
    links = getLinks(content, domain)
    metas = getMetas(content)
    return {
        'length': str(len(content)) + ' h1: ' + metas['h1'],
        'links': links
    }

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    url = request.form.get('link')
    return startScanAjax(url)


if __name__ == '__main__':
    app.run()
