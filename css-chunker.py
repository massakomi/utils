import re
from utils.init import loadUrl


class Chunker:
    def __init__(self):
        self.chunk = ''
        self.chunks = []
        self.chunkType = 'text'

    def save(self, newType):
        if self.chunk:
            print(f' save {self.chunkType} (next {newType})', end='')
            self.chunks.append([self.chunkType, self.chunk])
            self.chunk = ''
        else:
            print(f' start {newType} (old {self.chunkType})', end='')
        self.chunkType = newType

def extractCssChunks(content):
    i = 0
    ch = Chunker()
    while i < len(content):
        s = content[i:i+1]
        s2 = content[i:i+2]
        print(f'- {s}', end='')
        # Импорт
        if content[i:i+7] == '@import':
            ch.save('import')
        if s == ';' and ch.chunkType == 'import':
            ch.chunk += s
            s = ''
            ch.save('text')
        # Комментарий
        if s2 == '/*':
            ch.save('comment')
        if s2 == '*/':
            ch.chunk += s2
            s = ''
            i += 1
            ch.save('text')
        # Media старт
        if content[i:i + 6] == '@media':
            print(' MEDIA ', end='')
        if ch.chunkType == 'text':
            if content[i:i+6] == '@media':
                ch.save('mediaIn')
        if ch.chunkType == 'mediaIn' and s == '{':
            ch.chunk += s
            s = ''
            ch.save('text')
        # Media завершение
        if ch.chunkType == 'mediaOut':
            ch.save('text')
            print('')
            continue
            # здесь сразу следующем может идти не text (пробел), а сразу же mediaIn
        if ch.chunkType == 'text' and s == '}':
            ch.save('mediaOut')
        # Стили
        if ch.chunkType == 'text' and re.match(r'[a-z#.\[]', s, re.I):
            ch.save('style')
        if ch.chunkType == 'style' and s == '}':
            ch.chunk += s
            s = ''
            ch.save('text')
        ch.chunk += s
        i += 1
        print('')
    ch.save('')
    return ch.chunks

def mediaCode(style):
    matches = re.findall(r'([a-z-]+)\s*:\s*(\d+)', style.lower(), re.I)
    sizes = []
    for res in matches:
        sizes.append(res[0] + '=' + res[1])
    sizes = sorted(sizes)
    return ' '.join(sizes)

def printCssAsTable(chunks):
    doubles, doublesAll = [], []
    currentMedia = ''
    for chunk in chunks:
        type, style = chunk
        if type == 'text':
            continue
        if type == 'mediaIn':
            currentMedia = mediaCode(style)
        if type == 'mediaOut':
            currentMedia = ''
        stylec = re.sub(r'[\s;]*', '', style, re.I)
        if type == 'style':
            code = stylec + currentMedia
            if code in doublesAll:
                doubles.append(code)
            else:
                doublesAll.append(code)
    currentMedia = ''
    for chunk in chunks:
        type, style = chunk
        #if type == 'text':
        #    continue
        if type == 'mediaIn':
            currentMedia = mediaCode(style)
        if type == 'mediaOut':
            currentMedia = ''
        stylec = re.sub(r'[\s;]*', '', style, re.I)
        if type == 'style':
            code = stylec + currentMedia
            if code in doubles:
                # style
                del doubles[doubles.index(code)]
        print(type, style)

css = 'https://pythonworld.ru/m/css/st.css'
#content = loadUrl(css)
content = '@media f{.x{x}}@media f{.bookcardwrapper{x}}'
chunks = extractCssChunks(content)
print('')
print('-'*10)
printCssAsTable(chunks)