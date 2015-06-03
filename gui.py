from Tkinter import *
from ttk import *
from ansicolortext import AnsiColorText as ansi


class Connector(Toplevel):
     def __init__(self, parent):
        Toplevel.__init__(self, parent)   
        self.title('Connect to MUD')
        Label(self, text="Address").grid(row=0)
        Label(self, text="Port").grid(row=1)
        e1 = Entry(self)
        e2 = Entry(self)
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e1.insert(10,"localhost")
        e2.insert(10,"4004")
        
        button = Button(self, text='Connect')
        button.grid(row=3, column=1, sticky=W, pady=4)
        
        self.e1 = e1
        self.e2 = e2
        self.button = button
        
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
        self.initUI()

    def initUI(self): 
        tab1 = _Tab1(self)
        self.tab1 = tab1
        self.add(tab1, text = "Text")
        self.pack(fill=BOTH, expand=1)
        
class  _Tab1(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)   
        self.parent = parent
        self.initUI()

    def initUI(self):
        T = ansi(self)
        T.pack(fill=BOTH, expand=1)
        T.configure(state="disabled")
        E = Entry(self)
        E.pack(fill=X)
        E.focus()
        
        self.E = E
        self.T = T