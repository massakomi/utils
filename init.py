import datetime
import hashlib
import json
import os
import pprint
import re
import urllib
from typing import Optional
from urllib.parse import urlparse, urljoin

import requests
from numpy.f2py.auxfuncs import throw_error
from requests.auth import HTTPBasicAuth
from strip_tags import strip_tags
import re
from urllib.parse import urlparse, urljoin

import requests
from strip_tags import strip_tags


def utf(s):
    return s.encode('windows-1251').decode('utf-8')

def win(s):
    return s.encode('utf-8').decode('windows-1251')

def mb_ucfirst(s):
    return s.capitalize()

def url(add = '', query = ''):
    """
    РЕДАКТИРОВАНИЕ УРЛА
    url('id=5') - добавит к текущему QUERY_STRING. в случае если уже есть id - заменит
    url('id=5', 'id=10&mode=5')
    :param add:
    :param query:
    :return:
    """
    path = '' # _SERVER['SCRIPT_NAME']
    #query = query == '' ? _SERVER['QUERY_STRING']: query
    if query == '':
        return path + '?' + add
    currentAssoc = dict(urllib.parse.parse_qsl(query))
    addAssoc = dict(urllib.parse.parse_qsl(add))
    currentAssoc = currentAssoc | addAssoc

    a = []
    for key, value in currentAssoc.items():
        a.append(key if value == '' else f'{key}={value}')
    return path + '?' + '&'.join(a)



# ----------------------------------------------------------------------------------------------------------------------
# File Url load curl

def extension(filename):
    return os.path.splitext(filename)[1][1:]

def loadData():
    global FILEDATA
    with open(FILEDATA, "r") as file:
        data = json.load(file)
    return data

def saveData(data):
    global FILEDATA
    with open(FILEDATA, 'w') as file:
        json.dump(data, file)

def scanFiles(dir, opts=None):
    if opts is None:
        opts = {}
    if not os.path.exists(dir):
        return []
    data = []
    with os.scandir(dir) as it:
        for entry in it:
            path = entry.path
            if 'onlyDirs' in opts and not os.path.isdir(path):
                continue
            if 'onlyFiles' in opts and os.path.isdir(path):
                continue
            if 'utf' in opts:
                path = utf(path)
            data.append(path)
    return data

class cacher(object):
    content = ''
    cache = True
    expired = 0
    url = ''
    def __init__(self, url, cache, expired, ext=False):
        self.url = url
        self.cache = cache
        self.expired = expired
        self.ext = ext

    def __enter__(self):
        # print('enter')
        md5 = hashlib.md5(self.url.encode('utf-8')).hexdigest()
        self.fileName = 'cache/' + md5 + '.html'
        if self.cache and os.path.exists(self.fileName):
            # print(f'exist, expired = {self.expired}')
            time = datetime.datetime.now().timestamp()
            content = ''
            if self.expired == 0 or os.path.getmtime(self.fileName) >= time - self.expired:
                # print('read expired')
                with open(self.fileName, "r", encoding="utf-8") as file:
                    if self.ext:
                        self.content = json.load(file)
                    else:
                        self.content = file.read()
                content = self.content if not self.ext else self.content[0]
                if content == '':
                    print('Удаляю файл кэша, пустой контент')
                    os.remove(self.fileName)
            if content.find('Мы обнаружили, что запросы') > -1:
                self.content = ''
        return self

    def __exit__(self, type, value, traceback):
        if self.content == '' or not self.cache:
            return False
        if not os.path.exists('cache'):
            os.mkdir('cache')
        with open(self.fileName, "w", encoding="utf-8") as file:
            if self.ext:
                json.dump(self.content, file, ensure_ascii=False)
            else:
                file.write(self.content)

def loadUrlEx(url: str, cache: bool=True, expired: int =0):
    with cacher(url, cache, expired, ext=True) as cache:
        if not cache.content:
            cache.content = curlLoad(url, ext=True)
    return cache.content

def loadUrl(url: str, cache: bool =True, expired: int =0):
    with cacher(url, cache, expired) as cache:
        if not cache.content:
            cache.content = curlLoad(url)
    return cache.content

def curlLoad(url: str, post: Optional[dict] =None, ext: bool=False):
    global curlOpts
    if 'curlOpts' not in globals():
        curlOpts = {}
    if post is None:
        post = {}
    if not url:
        return ''

    print(f'curlLoad {url}')

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:43.0) Gecko/20100101 Firefox/43.0"
    }

    auth = None
    if 'user' in curlOpts and 'password' in curlOpts:
        auth = HTTPBasicAuth('user', 'password')

    try:
        if post:
            response = requests.post(url, data=post, headers=headers, auth=auth)
        else:
            response = requests.get(url, headers=headers, auth=auth)
    except Exception as e:
        print(f'Ошибка - {str(e)} ({type(e).__name__})')
        return ''

    # print(response.status_code)
    # print(response)

    content = response.text
    if ext:
        location = ''
        if 'Location' in response.headers:
            location = response.headers['Location']
        return [content, response.status_code, location, response.headers['Content-Type']]
    else:
        return content


def curlHeader(url):
    response = requests.head(url)
    content = response.text
    return response.headers

u = 'https://mksmedia.ru/'
print(curlHeader(u))

def getHttpStatus(url):
    response = requests.get(url)
    return response.status_code



# ----------------------------------------------------------------------------------------------------------------------
# SEO

def getLinks(content, link, opts=None):
    """
    Извлечь уникальные ссылки из контента в абсолютном виде
    :param content:  контент страницы
    :param link:  - базовый урл, чтобы правильно обработать относительные ссылки
    :param opts:
    :return:
    """
    if opts is None:
        opts = {}
    if not hasattr(getLinks, 'unique'):
        getLinks.unique = []

    matches = re.findall(r'\s+href\s*=\s*["\'](.*?)["\']', content, re.I | re.S)

    matches2 = re.findall(r'location=\'(.*?)\'', content, re.I | re.S)
    links = list(set(matches + matches2))
    links = sorted(links)

    a = urlparse(link.lower())
    host = a.hostname

    output = []
    for urlOrig in links:
        hash = urlOrig.find('#')
        if hash > -1:
            # print(urlOrig, end=' -> ')
            urlOrig = urlOrig[0:hash]
        url = urlOrig.strip()
        if not url:
            continue
        # Пропускаем урлы не этого сайта
        if url.startswith('http') or url.startswith('www'):
            if host not in url:
                continue

        # Очищаем урл от http/www.host
        url = re.sub(rf'https?://(www.)?{host}', '', url, re.I | re.U)

        # Пропускаем ссылки ненужные
        if (url.startswith('mailto') or url.startswith('viber:') or url.startswith('skype:') or url.startswith('tel:') or url.startswith('?')
                or url.startswith('@') or url.startswith('javascript:') or url.find('.css') > -1):
            continue
        if opts.get('skip_index_query') and url.startswith('/?'):
            continue
        if opts.get('skip_filter') and opts.get('skip_filter') in url:
            continue

        # Относительные урлы обработка
        urlFull = urljoin(link, url)

        # Пропуск дублей
        uniq = url
        if opts.get('skip_numerical_dupl'):
            uniq = re.sub(r'\d+', '', uniq)
        if (uniq in getLinks.unique) or (urlFull == link):
            continue
        getLinks.unique.append(uniq)
        output.append(urlFull)

    output = sorted(output)
    return output

def w3cErrors(url, cache=False):
    checkUrl = 'https://validator.w3.org/nu/?doc=' + url
    # content = loadUrl(checkUrl, cache) # content.count('<li class="error">')
    return [checkUrl, 'не работает, блокировка']

def getMetas(content):
    if not hasattr(getMetas, 'errors'):
        getMetas.errors = []

    matches = re.findall(r'<h1[^>]*>(.*?)</h1>', content, re.I | re.S)
    h1 = '' if not matches else strip_tags(matches[0])
    if len(matches) > 1:
        getMetas.errors.append(f'Больше двух h1 на странице ({strip_tags(' '.join(matches))})')

    res = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
    title = res[1] if res else ''
    res = re.search(r'<meta\s*name="description"\s*content="(.*?)"', content, re.I | re.S)
    description = res[1] if res else ''
    res = re.search(r'<meta\s*name="keywords"\s*content="(.*?)"', content, re.I | re.S)
    keywords = res[1] if res else ''
    res = re.search(r'<meta\s*name="robots"\s*content="(.*?)"', content, re.I | re.S)
    robots = res[1] if res else ''

    if content.find('breadcrumb'):
        res = re.search(r'<(div|ul) class="breadcrumbs?".*?</(div|ul)>\s*</div>', content, re.I | re.S)
        bread = res[0] if res else ''
        matches = re.findall(r'<span itemprop="name">(.*?)</span>', bread, re.I | re.S)
        breads = [x.strip() for x in matches]
        breads = ' / ' . join(breads)

    return dict(zip(['h1', 'title', 'description', 'keywords', 'breads', 'robots'], [h1, title, description, keywords, breads, robots]))


def getAttr(attr, content):
    res = re.search(rf'{attr}="([^"]+)"', content, re.I | re.S)
    return res[1] if res else ''

def getImgs(content):
    imgs = re.findall(r'<img [^>]+>', content, re.I | re.S)
    imgsLocal = {}
    for img in imgs:
        src = getAttr('src', img)
        alt = getAttr('alt', img)
        title = getAttr('title', img)
        imgsLocal [src] = (alt, title)
    return imgsLocal

def getImages(content):
    """
    Извлекает из контента картинки и разбирает их по тегам
     (нужно было для извлечения и сравнения альтов картинок, правильно ли прописаны в контенте материала и в тестовом файле)
    :param content:
    :return:
    """
    imgsDb = re.findall(r'<img[^>]+>', content, re.I)
    imgsDbStr = {}
    for res in imgsDb:
        b = re.findall(r'(src|title|alt)\s*=\s*"([^"]+)"', res, re.I | re.S)
        ats = {}
        for (attr, value) in b:
            if attr == 'src':
                value = re.sub(r'^/', '', value)
            ats [attr] = value.strip()
        if 'src' not in ats:
            raise Exception(f'Не найден src в {res}')
        imgsDbStr [ats['src']] = ats
    return imgsDbStr

def htmlspecialchars(text):
    return text \
    .replace(u"&", u"&amp;") \
    .replace(u'"', u"&quot;") \
    .replace(u"'", u"&#039;") \
    .replace(u"<", u"&lt;") \
    .replace(u">", u"&gt;")

def compareValues(altLocal, altRemote, text):
    add = ''
    eq = altLocal.strip() == altRemote.strip()
    if not eq:
        add = f'title="{htmlspecialchars(altLocal)} != {htmlspecialchars(altRemote)}"'
    return f' <span{add} style="color:{'green' if eq else 'red'}">{text}</span>'

def comparePrepare(content):
    return re.sub(r'[^а-яa-z_-]', '', content, re.I | re.U)

def isEqual(a, b):
    return comparePrepare(a) == comparePrepare(b)


# ----------------------------------------------------------------------------------------------------------------------
# HTML

def selector(data, attrs, opts=None):
    if opts is None:
        opts = {}
    str = f'<select{attrs}>'
    if 'empty' in opts:
        str += f'<option value="">{opts['empty']}</option>'
    for key, value in data.items():
        add = f' value="{key}"'
        if 'values' in opts and not opts['values']:
            add = ''
        str += f'<option{add}>{value}</option>'
    str += f'</select>'
    return str

def printArrayTable(data):
    print('<style type="text/css">'
          'table.tt empty-cells:show; border-collapse:collapse; ; margin:10px 0;'
          'table.tt td border:1px solid #ccc; padding: 3px; vertical-align: top;'
          'table.tt tr:nth-child(odd) background-color:#eee; '
          '</style>')
    print('<table class="tt">')
    for values in data:
        print('<tr>')
        for v in values:
            print('<td>' + v +'</td>')
        print('</tr>')
    print('</table>')

def addRow(data, t='td', st='', ats=None):
    if ats is None:
        ats = {}
    str = "\n" + '<tr' + st + '>'
    for k, v in data:
        add = ''
        if k in ats:
            add = ' ' + ats[k]
        str += "\n" + '    <' + t + '' + add + '>' + v + '</' + t + '>'
    str += "\n" + '</tr>'
    return str


# ------------------------------------------------------------------------------------------------------------
# TEXT Diff

def getTextDiff(textA, textB, delimiter = "\n"):
    """
    Выделение различий в текстах (с точностью до строк или слов)
    Изменения оборачиваются в тег "span" с классами 'added', 'deleted', 'changed
    алгоритм: http://easywebscripts.net/php/php_text_differences.php
    :param textA:
    :param textB:
    :param delimiter:
    :return:
    """
    pass



#print(selector({'x': 1}, ' name="xx"'))

# url = 'https://mksmedia.ru/sozdaniye-saytov/'
# content = loadUrl(url)

# imgs = getImages(content)
# pprint.PrettyPrinter(depth=4, indent=4, width=150).pprint(imgs)





def pr(data):
    pprint.PrettyPrinter(depth=4, indent=2, width=150).pprint(data)