# MinecraftLogViewer by FlyModeZ

import gzip
import os
import re
import sys
import ctypes
ctypes.OleDLL("shcore").SetProcessDpiAwareness(1)#idlelib.pyshell


from idlelib.run import fix_scaling
from tkinter.constants import *
from tkinter import ttk
import tkinter as tk

info = {
    "enablere": "启用正则表达式",
    "find": "查找",
    "justfind": "{name} 于 {find}",
    "per": "{i}/{count}",
    "reerror": "正则表达式错误"
    }

class File:
    def __init__(self):
        pass

    def scan(self, path=None):
        l = []
        for i in os.listdir(path):
            if i[-3:] in ("log", ".gz"): l.append(i)
        return l

    def open(self, name):
        return gzip.open(name) if name[-3:] == ".gz" else open(name, "rb")

class Finder:
    def __init__(self, file, frame, text):
        self.file = file
        self.frame = frame
        self.text = text
        self.entry = ttk.Entry(self.frame, width=30)
        self.entry.bind("<Return>", self.find)
        self.entry.pack(side=LEFT)
        self.re = tk.BooleanVar(self.frame)
        self.checkbutton = ttk.Checkbutton(self.frame, text=info["enablere"], variable=self.re)
        self.checkbutton.bind("<Return>", self.find)
        self.checkbutton.pack(side=LEFT)
        self.button = ttk.Button(self.frame, text=info["find"], command=self.find)
        self.button.pack(side=LEFT)
        self.label = ttk.Label(self.frame, width=20)
        self.label.pack(side=LEFT)
        self.progrerssbar = ttk.Progressbar(self.frame, length=300)
        self.progrerssbar.pack(side=LEFT)
        self.label2 = ttk.Label(self.frame, width=20)
        self.label2.pack(side=LEFT)

    def find(self, event=None):
        self.pattern = self.entry.get()
        self.mode = self.re.get()
        self.lst = self.file.scan()
        self.count = len(self.lst)
        self.progrerssbar.config(maximum=self.count)
        self.text.delete("0.0", END)
        if self.mode:
            try:
                re.compile(self.pattern)
            except re.error:
                self.show(info["reerror"])
                return
        self._find(1)

    def _find(self, i):
        if i == self.count: return
        name = self.lst[i]
        self.label.config(text=name)
        text = self.file.open(name).read().decode("ansi", errors="ignore")
        l = self._find_re(text) if self.mode else self._find_only(name, text)
        for t in l:
            self.show(t)
        self.progrerssbar.step(1)
        self.label2.config(text=info["per"].format(i=i + 1, count=self.count))
        self.frame.after("idle", self._find, i + 1)

    def _find_only(self, name, text):
        find = -1
        while True:
            find = text.find(self.pattern, find + 1)
            if find == -1: break
            yield info["justfind"].format(name=name, find=find)

    def _find_re(self, text):
        return re.findall(self.pattern, text)

    def show(self, text):
        self.text.insert(END, text + "\n")
        #w.textscrollbar.set(1, 1)# ?

class Window:
    def __init__(self):
        self.lastname = ""
        self.file = File()
        self.window = tk.Tk(screenName=None)
        self.window.title("MinecraftLogViewer v0.1.0  -- FlyMode")

        #tk.PanedWindow(
        self.listboxframe = tk.Frame(self.window)
        self.listbox = tk.Listbox(self.listboxframe, height=36, width=20)
        self.listboxscrollbar = tk.Scrollbar(self.listboxframe, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.listboxscrollbar.set)
        self.listbox.pack(side=LEFT, fill=BOTH)
        self.listboxscrollbar.pack(side=RIGHT, fill=Y)
        self.textframe = tk.Frame(self.window)
        self.text = tk.Text(self.textframe, font=("黑体", 10), height=45, width=160)
        self.textscrollbar = tk.Scrollbar(self.textframe, command=self.text.yview)
        self.text.config(yscrollcommand=self.textscrollbar.set)
        self.text.pack(side=LEFT, fill=BOTH)
        self.textscrollbar.pack(side=RIGHT, fill=Y)

        self.findframe = tk.Frame(self.window)
        self.finder = Finder(self.file, self.findframe, self.text)

        self.findframe.pack(side=TOP)
        self.listboxframe.pack(side=LEFT)
        self.textframe.pack(side=LEFT)

        self.window.update()
        self.l_update()
        self.t_update()

    def mainloop(self):
        self.window.mainloop()

    def l_update(self):
        for i in self.file.scan():
            self.listbox.insert(END, i)

    def t_update(self):
        name = self.listbox.get(ACTIVE)
        if name != self.lastname:
            self.lastname = name
            try:
                file = self.file.open(name)
            except FileNotFoundError:
                pass
            else:
                self.text.delete("0.0", END)
                self.text.insert("0.0", file.read().decode("ansi"))
        self.window.after(25, self.t_update)


w = Window()

w.mainloop()

#\n(.*?nb2.*?(?:凋零|凋灵).*?)\n
