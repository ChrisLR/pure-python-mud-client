from tkinter import *
from tkinter.ttk import *
from ansicolortext import AnsiColorText


class Connector(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title('Connect to MUD')
        Label(self, text="Address").grid(row=0)
        Label(self, text="Port").grid(row=1)
        self.entry_1 = Entry(self)
        self.entry_2 = Entry(self)
        self.entry_1.grid(row=0, column=1)
        self.entry_2.grid(row=1, column=1)
        self.entry_1.insert(10, "localhost")
        self.entry_2.insert(10, "4004")

        self.button = Button(self, text='Connect')
        self.button.grid(row=3, column=1, sticky=W, pady=4)


class View(Toplevel):
    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.title('PyMud')
        self.geometry("1280x768")
        self.Tabs = _Tabs(self)


class _Tabs(Notebook):
    def __init__(self, parent):
        Notebook.__init__(self, parent)
        self.parent = parent
        self.tab1 = None
        self.initialize_ui()

    def initialize_ui(self):
        self.tab1 = _Tab1(self)
        self.add(self.tab1, text="Text")
        self.pack(fill=BOTH, expand=1)


class _Tab1(Frame):
    def __init__(self, parent):
        super().__init__()
        Frame.__init__(self, parent)
        self.entry = None
        self.ansi_text = None
        self.parent = parent
        self.initialize_ui()

    def initialize_ui(self):
        self.ansi_text = AnsiColorText(self)
        self.ansi_text.pack(fill=BOTH, expand=1)
        self.ansi_text.configure(state="disabled")
        self.entry = Entry(self)
        self.entry.pack(fill=X)
        self.entry.focus()
