import json
import os
import pprint
import random
import tkinter.constants
from tkinter import ttk, font
from tkinter import *
from tkinter.scrolledtext import ScrolledText

import humanize


class Files:

    def __init__(self):
        pass

    def scan(self, path):
        total = 0
        files = []
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    size = self.dirSize(entry.path)
                else:
                    size = os.path.getsize(entry.path)
                total += size
                files.append({
                    'name': entry.name,
                    'dir': '0' if entry.is_dir() else '1',
                    'path': entry.path,
                    'size': size,
                })

        files = sorted(files, key=lambda item: item['dir'] + item['name'])
        # print(json.dumps(files, indent=4))
        return files

    def dirSize(self, path):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    size = os.path.getsize(entry.path)
                    total += size
                else:
                    total += self.dirSize(entry.path)
        return total

class FolderStat:

    def __init__(self):
        self.buildForm()
        self.input = None

    def buildForm(self):

        root = Tk()
        root.title("Folder Stat")
        root.geometry("800x600+200+200")
        root.columnconfigure(index=0, weight=1)
        root.rowconfigure(index=0, weight=1)
        root.rowconfigure(index=1, weight=20)

        self.form()
        self.table()
        root.mainloop()

    def form(self):
        frame = ttk.Frame()
        frame.grid(row=0, column=0)

        self.input = ttk.Entry(frame, width=60)
        self.input.grid(row=0, column=0, padx=6, pady=6)
        self.input.insert(0, r'G:\python\test\utils\php\data')

        open_button = ttk.Button(frame, text="Показать статистику", command=self.processFile)
        open_button.grid(row=0, column=1)

    def table(self):
        path = self.input.get()
        data = []
        self.files = Files().scan(path)
        for item in self.files:
            size = humanize.naturalsize(item['size'])
            row = [item['dir'], item['name'], size]
            data.append(row)

        columns = {
            "type": "#",
            "name": "Имя",
            "size": "Размер",
        }
        Table(data, columns)

    def processFile(self):
        self.table()


class Table:

    def __init__(self, data, columns):

        self.tree = ttk.Treeview(columns= tuple(columns.keys()), show="headings")
        self.tree.grid(row=1, column=0, sticky="nsew")

        index = 0
        for key, value in columns.items():
            self.tree.heading(key, text=value, command=lambda x=index: self.sort(x, False))
            index += 1

        self.tree.column("#1", stretch=NO, width=20)

        # теги
        bold_font = font.Font(family="Arial", size=9, weight="bold")
        self.tree.tag_configure("bold", font=bold_font)

        for row in data:
            tags = ("bold") if row[0] == '0' else ()
            row[0] = 'd' if row[0] == '0' else ''
            self.tree.insert("", END, values=row, tags=tags)

        # добавляем вертикальную прокрутку
        scrollbar = ttk.Scrollbar(orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")

        self.events()

    def events(self):
        def item_selected(event):
            selected_people = ""
            for selected_item in self.tree.selection():
                item = self.tree.item(selected_item)
                person = item["values"]
                selected_people = f"{selected_people}{person}\n"
            print(selected_people)
            #label["text"] = selected_people

        self.tree.bind("<<TreeviewSelect>>", item_selected)
        self.tree.bind("<Double-1>", item_selected)

    def sort(self, col, reverse):
        # получаем все значения столбцов в виде отдельного списка
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        # сортируем список
        l.sort(reverse=reverse)
        # переупорядочиваем значения в отсортированном порядке
        for index, (_, k) in enumerate(l):
            self.tree.move(k, "", index)
        # в следующий раз выполняем сортировку в обратном порядке
        self.tree.heading(col, command=lambda x=col: self.sort(x, not reverse))


FolderStat()

"""


"""