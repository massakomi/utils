import re
import sys

with open("data/crontab.txt", "r") as file:
    for line in file:
        line = line.strip()
        if line == '' or line.startswith("#"):
            continue
        m = r'[\d/\\\,*]+'
        res = re.fullmatch(rf'({m})\s+({m})\s+({m})\s+({m})\s+({m})\s+(.*)', line)
        if res is None:
            print(f'error {line}')
            sys.exit()

        min, hour, day, month, dayOfWeek, *other = res.groups()

        print(line)
        print(f'минута {min} час {hour} день {day} месяц {month} день недели {dayOfWeek}')
        print('-' * 80)
