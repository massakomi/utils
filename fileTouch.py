import datetime
import os
import re
from tkinter import *
from tkinter import ttk


class FileManage:
    def __init__(self, form):
        self.form = form

    @staticmethod
    def collectFolders(path, include_subdirs):
        folders = [path]
        if include_subdirs:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_dir():
                        folders.append(entry.path)
        return folders

    @staticmethod
    def collectFiles(folders):
        files = []
        for path in folders:
            with os.scandir(path) as it:
                for entry in it:
                    if entry.is_file():
                        files.append({
                            'name': entry.name,
                            'path': entry.path,
                        })
        return files

    def filePrepare(self, filename):
        operation = self.form.operation.get()
        if operation == 'lower':
            filename = filename.lower()
        if operation == 'upper':
            filename = filename.upper()
        if operation == 'capitalize':
            filename = filename.capitalize()
        replace_from = self.form.replace_from.get()
        replace_to = self.form.replace_to.get()
        if replace_from:
            filename = filename.replace(replace_from, replace_to)
        return filename

    def fileProcess(self, path, old, new):
        if old != new:
            dir = os.path.splitext(path)[0]
            newPath = os.path.join(dir, new)
            if not os.path.exists(newPath):
                os.rename(path, newPath)
                path = newPath

        set_date = self.form.set_date.get()
        if set_date:
            try:
                date = datetime.datetime.strptime(set_date, '%Y-%m-%d')
                timestamp = date.timestamp()
                os.utime(path, (timestamp, timestamp))
            except Exception as e:
                print('Ошибка выполнения ('+type(e).__name__+')')

    def filter(self, files):
        extensionFilter = self.form.extension.get()
        for file in files:
            old = file['name']
            if extensionFilter:
                extensionFilter = re.sub(r'[^a-z\d]', '', extensionFilter).lower()
                extension = os.path.splitext(old)[1][1:].lower()
                if extension != extensionFilter:
                    print(f'{extension} != {extensionFilter}')
                    continue
            yield file

    def exec(self, confirm=True):

        path = self.form.path.get()
        if not os.path.exists(path):
            raise FileNotFoundError

        # собираем подпапки
        folders = self.collectFolders(path, self.form.include_subdirs)

        # собираем пути файлов
        files = self.collectFiles(folders)
        sorted(files, key=lambda item: item['name'])

        output = []
        for file in self.filter(files):
            path = file['path']
            old = file['name']
            new = self.filePrepare(old)
            if confirm:
                self.fileProcess(path, old, new)
            output.append(f'{old} -> {new}')

        self.form.results.set("\n".join(output))

    def view(self):
        self.exec(confirm=False)

class Display:
    def __init__(self):
        self.path = StringVar()
        self.include_subdirs = IntVar()
        self.extension = StringVar()
        self.operation = StringVar()
        self.replace_from = StringVar()
        self.replace_to = StringVar()
        self.set_date = StringVar()
        self.results = StringVar()

    @staticmethod
    def create_gridded_frame(x = 5, y = 3):
        frame = ttk.Frame(borderwidth=1, relief=SOLID, padding=[3, 3])
        frame.pack(anchor=NW, fill=X, padx=5, pady=5)
        for c in range(x): frame.columnconfigure(index=c, weight=1)
        for r in range(y): frame.rowconfigure(index=r, weight=1)
        return frame

    @staticmethod
    def grid(obj, position):
        sticky = W
        if len(position) == 2:
            position.append(1)
        if len(position) == 5:
            sticky = position.pop()
        if len(position) == 4:
            width = position.pop()
            obj.config(width=width)
        params = dict(zip(['row', 'column', 'columnspan'], position))
        obj.grid(**params, pady=(0, 3), sticky=sticky)

    def add_text_input(self, frame, position: list, textvariable: StringVar, default: str = '') -> None:
        input = ttk.Entry(frame, textvariable=textvariable)
        if default:
            input.insert(0, default)
        self.grid(input, position)

    def add_checkbox(self, frame, position: list, text, variable):
        chbx = ttk.Checkbutton(frame, text=text, variable=variable)
        self.grid(chbx, position)

    def add_button(self, frame, position: list, command, text):
        btn = ttk.Button(frame, text=text, command=command)
        self.grid(btn, position)

    def add_label(self, frame, position: list, text):
        label = ttk.Label(frame, text=text)
        self.grid(label, position)

    def add_select(self, frame, position: list, values: list, textvariable):
        combobox = ttk.Combobox(frame, textvariable=textvariable, values=values)
        self.grid(combobox, position)

    def build(self):
        frame = self.create_gridded_frame(5, 4)

        self.add_text_input(frame, [0, 0, 5, 100], self.path, r'G:\python\test\data')

        self.add_label(frame, [1, 0], 'Только с расширением:')
        self.add_text_input(frame, [1, 1, 1, 5], self.extension)
        self.add_checkbox(frame, [1, 2], "Включая подпапки", self.include_subdirs)
        list = ['операция', 'lower', 'upper', 'capitalize']
        self.add_select(frame, [1, 3], list, self.operation)

        self.add_label(frame, [2, 0], 'Заменить:')
        self.add_text_input(frame, [2, 1, 1, 20], self.replace_from)
        self.add_text_input(frame, [2, 2, 1, 20], self.replace_to)

        self.add_label(frame, [3, 0, 1, 20], 'Изм-ть дату (Y-m-d):')
        self.add_text_input(frame, [3, 1], self.set_date)

        file = FileManage(self)
        self.add_button(frame, [4, 0], file.exec, 'Выполнить')
        self.add_button(frame, [4, 1], file.view, 'Показать')

        # result message
        label = Label(text="", textvariable=self.results, justify=LEFT)
        label.pack(anchor=NW, side=LEFT)


root = Tk()
root.title('File changer')
root.geometry("600x400+400+200")
form = Display()
form.build()
root.mainloop()