import pprint
import re
import sys
from collections import defaultdict

from utils.init import loadUrl, pr

def getSiteCssFiles(siteUrl):
    """
    По урл сайта возвращает список урлов файлов стилей
    """
    if not siteUrl.endswith('/'):
        siteUrl = siteUrl + '/'
    pos = siteUrl.index('/', 9)
    site = siteUrl[:pos+1]

    content = loadUrl(siteUrl)

    pattern = r'rel="?stylesheet"? href\s*=\s*[\'"]?([^\'">\s]+)\s*[\'"]?'
    matches = re.findall(pattern, content)
    cssFiles = []
    for cssurl in matches:
        if not cssurl.startswith('http'):
            cssurl = site + re.sub(r'^/', '', cssurl)
        if 'jquery' in cssurl:
            continue
        cssFiles.append(cssurl)

    #for i in matches:

    return cssFiles


url = 'https://pythonworld.ru/moduli'
num = 0

if not url:
    while True:
        url = input('Загрузка css файлов. Напишите адрес сайта: ')
        if not url.startswith('http') or len(url) < 13 or not '.' in url:
            print('Неправильный урл')
            continue
        print('Список файлов:')
        cssFiles = getSiteCssFiles(url)
        for index, css in enumerate(cssFiles):
            print(f'[{index + 1}] {css}')
        while True:
            num = input('Укажите номер файла: ')
            if not num.isdigit() or num == '' or int(num) < 1:
                print('Нужно написать число')
            elif int(num) > len(cssFiles):
                print('Не найден файл по числу')
            else:
                print(f'Выбран файл: {cssFiles[int(num) - 1]}')
                break

cssFiles = getSiteCssFiles(url)
file = cssFiles[num]
content = loadUrl(file)

# Чистка от media
rx = re.compile(r'(@media([^{]+)\{.*?}\s*})', re.I | re.S)
#matches = re.findall(rx, content)
content = re.sub(rx, '', content)

# Извлечение всех стилей
matches = re.findall(r'([=\s\da-z.,#:>"\'\]\[)(+*_-]+)\{([^}]+)', content, re.I | re.S)

# Проверка
cnt = content.count('{')
if cnt != len(matches):
    print(f'Ошибка разбора {cnt} != {len(matches)}')


def deCommaList(matches: list) -> dict:
    """
    Расклеиваем стили с запятыми
    """
    output = defaultdict(list)
    for (rule, style) in matches:
        if ',' in rule:
            for subRule in rule.split(','):
                output[subRule].append(style)
        else:
            output[rule].append(style)
    return dict(output)

def getStyleData(styles):
    """
    Преобразует текстовый список правил в массив
    """
    styleData = {}
    for style in styles:
        styleBlocks = re.split(r'\s*;\s*', style)
        for block in styleBlocks:
            if block == '':
                continue
            param, value = re.split(r'\s*:\s*', block)
            if param == '':
                continue
            styleData [param] = value
    return styleData

def simpleStyleTree(rules):
    """
    Просмотр дерева стилей в виде списка
    """
    tree = {}
    for rule, styles in rules.items():
        base = rule
        if ' ' in rule:
            base = rule[0:rule.index(' ')]
        styleData = getStyleData(styles)
        tree [base] = styleData
    return tree

rules = deCommaList(matches[:10])
tree = simpleStyleTree(rules)
pr(tree)


