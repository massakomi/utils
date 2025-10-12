import os
import sys
import humanize
import win32api

class FileManager:

    def __init__(self):
        self.disk = ''
        self.folder_num = -1
        self.__dirs__ = []

    @staticmethod
    def drives_list():
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        drivesMenu = []
        for drive in drives:
            drivesMenu.append(f'{drive[0:-1]}')
        drivesMenu = ' '.join(drivesMenu)
        return drivesMenu

    @staticmethod
    def scandir_entries(path):
        entries = []
        with os.scandir(path) as it:
            for entry in it:
                entries.append({
                    'name': entry.name,
                    'size': humanize.naturalsize(entry.stat().st_size),
                    'file': 1 if entry.is_file() else 0,
                })
        return entries

    def scandir_sorted(self, path):
        entries = self.scandir_entries(path)
        entries = sorted(entries, key=lambda item: str(item['file']) + item['name'])
        return entries

    def print_dir(self, path):
        print('-' * 80)
        print(f'List of "{path}"')
        print('-' * 80)
        num = 0
        entries = self.scandir_sorted(path)
        for entry in entries:
            if entry["file"]:
                print(f'[file] {entry["name"]} {entry["size"]}')
            else:
                print(f'{entry["name"]} [{num}]')
                self.__dirs__.append(entry["name"])
                num += 1
        print('-' * 80)

    def print_current_dir(self):
        path = f'{self.disk}:\\'
        if self.folder_num >= 0:
            folder = self.__dirs__[self.folder_num]
            path += f'{folder}\\'
        self.print_dir(path)

    def test(self):

        print(self.__dirs__)

        # fm = FileManager()
        # entries = fm.scandir_sorted('E:\\')
        # import pprint
        # pprint.PrettyPrinter(depth=4, indent=4, width=150).pprint(entries)
        sys.exit()


fmanager = FileManager()
fmanager.disk = 'c'

# fm.print_dir(f'C:\\')
# fm.test()


while True:
    print(f'List of disks: {fmanager.drives_list()}')
    if fmanager.disk:
        fmanager.print_current_dir()
    value = input('Type disk symbol or folder number: ')
    if not value:
        break
    print(f'Your disk is {value}')
    if value.isalpha():
        fmanager.disk = value.capitalize()
        fmanager.folder_num = -1
        fmanager.print_current_dir()
    if value.isdigit():
        fmanager.folder_num = int(value)
        fmanager.print_current_dir()