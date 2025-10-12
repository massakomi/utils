import functools
import json
import pprint
import shutil
import tkinter.constants
from tkinter import Tk, filedialog, ttk, SE, NW, N, Label, Text, BOTH, StringVar, INSERT, WORD, LEFT, SOLID, X, BOTTOM
from tkinter.scrolledtext import ScrolledText
from typing import IO, Iterator
import openpyxl


global transformType, editor

def iter_excel_openpyxl(file: IO[bytes]) -> Iterator[dict[str, object]]:
    workbook = openpyxl.load_workbook(file, read_only=True)
    rows = workbook.active.rows
    for row in rows:
        yield [cell.value for cell in row]

def open_file():
    global transformType
    filepath = filedialog.askopenfilename(initialdir=r'G:\python\test\utils\php')
    if filepath != "":
        print(transformType.get())
        shutil.copy(filepath, 'data/file.xlsx')
        processFile()

def buildForm():
    global transformType, editor
    frame = ttk.Frame(borderwidth=1, relief=SOLID, padding=[2, 2])
    frame.pack(anchor=NW, fill=X, padx=5, pady=5)

    label = Label(frame, text="Преобразование excel файла")
    label.pack(anchor=N, padx=1, pady=1, side=LEFT)

    open_button = ttk.Button(frame, text="Открыть файл", command=open_file)
    open_button.pack(anchor=N, padx=1, pady=1, side=LEFT)

    transformType = StringVar(value='JSON')
    rb1 = ttk.Radiobutton(frame, text='JSON', value='JSON', variable=transformType)
    rb1.pack(anchor=N, padx=1, pady=1, side=LEFT)
    rb2 = ttk.Radiobutton(frame, text='PRINT', value='PRINT', variable=transformType)
    rb2.pack(anchor=N, padx=1, pady=1, side=LEFT)

    editor = ScrolledText(root, wrap = tkinter.constants.CHAR)
    editor.pack(fill=BOTH, padx=1, pady=1, expand=True)
    editor.config(font=("consolas", 10), undo=True)


def processCheck(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print('Ошибка выполнения (' + type(e).__name__ + ')')
        pass
    return wrapper

@processCheck
def processFile():
    with open('data/file.xlsx', 'rb') as f:
        rows = iter_excel_openpyxl(f)
        list = [row for row in rows]
        if transformType.get() == 'PRINT':
            pprint.PrettyPrinter(depth=4, indent=4, width=150).pprint(list)
        else:
            editor.insert(INSERT, json.dumps(list, ensure_ascii=False))

root = Tk()
root.title("Excel")
root.geometry("800x600+200+200")
buildForm()
processFile()
root.mainloop()