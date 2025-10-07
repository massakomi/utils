import datetime
import os
import pprint

import requests
import hashlib

def loadUrl(url, cache=True, expired=0):
    with cacher(url, cache, expired) as cache:
        if not cache.content:
            cache.content = curlLoad(url)
    return cache.content

class cacher(object):
    content = ''
    cache = True
    expired = 0
    url = ''
    def __init__(self, url, cache, expired):
        self.url = url
        self.cache = cache
        self.expired = expired

    def __enter__(self):
        # print('enter')
        md5 = hashlib.md5(self.url.encode('utf-8')).hexdigest()
        self.fileName = 'cache/' + md5 + '.html'
        if self.cache and os.path.exists(self.fileName):
            # print(f'exist, expired = {self.expired}')
            time = datetime.datetime.now().timestamp()
            if self.expired == 0 or os.path.getmtime(self.fileName) >= time - self.expired:
                # print('read expired')
                with open(self.fileName, "r", encoding="utf-8") as file:
                    self.content = file.read()
                if self.content == '':
                    print('Удаляю файл кэша, пустой контент')
                    os.remove(self.fileName)
            if self.content.find('Мы обнаружили, что запросы') > -1:
                # print('clear')
                self.content = ''
        return self

    def __exit__(self, type, value, traceback):
        if self.content == '' or not self.cache:
            return False
        if not os.path.exists('cache'):
            os.mkdir('cache')
        with open(self.fileName, "w", encoding="utf-8") as f:
            f.write(self.content)

def curlLoad(url):

    #return str(datetime.datetime.now())

    print(f'curlLoad {url}')
    response = requests.get(url)
    # print(response.status_code)
    # print(response)

    content = response.text
    return content

def pr(data):
    pprint.PrettyPrinter(depth=4, indent=2, width=150).pprint(data)