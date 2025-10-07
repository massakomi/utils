import re
import sys
from datetime import datetime

RED = '\033[91m'
BLUE = '\033[94m'
ENDC = '\033[0m'

# 127.0.0.1 - - [01/Sep/2024:11:23:31 +0300] "GET / HTTP/2.0" 200 8001 "https://yii2-films.site/"
# "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
with open("data/access.log", "r") as file:
    for line in file:
        #print(line, end="")
        res = re.match(r'\d+.\d+.\d+.\d+', line)
        if res is None:
            print(f'{RED}error ip: {line}')
            sys.exit()
        ip = res[0]

        res = re.search(r'(POST|GET) (.*?) HTTP/[\d.]*" (\d+) ([\d-]+) "(.*?)" "(.*?)"', line, re.I)
        if res is None:
            print(f'{RED}error read line: {line}')
            sys.exit()

        method, url, status, length, urlfull, agent, *misc = res.groups()

        res = re.search(r'\[(.*?)]', line)
        if res is None:
            print(f'{RED}error time: {line}')
            sys.exit()
        date = datetime.strptime(res[1], '%d/%b/%Y:%H:%M:%S %z')
        timestamp = date.timestamp()
        ymd = datetime.strftime(date, '%Y-%m-%d')
        hms = datetime.strftime(date, '%H:%M:%S')

        res = re.search(r'(jpg|png|css|js|txt|woff2|gif)(\?\d+)?$', line)
        if res is not None:
            print(f'{BLUE} image skip {line}{ENDC}')
            continue

        if status != '200':
            pass

        if date != lastDate:
            print(f'{BLUE} date: {date}')
        lastDate = ymd

        print(hms, ip, status, url, agent)

        #break