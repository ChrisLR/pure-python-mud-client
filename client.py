import sys
import threading
import queue
import socket
import tkinter
import gui


class Controller(object):
    def __init__(self, parent):
        self.host = None
        self.port = None
        self.input_queue = None
        self.output_queue = None
        self.view = None
        self.running = False
        self.thread1 = None
        self.socket = None
        self.parent = parent
        self.connect = gui.Connector(root)
        self.connect.button.config(command=self.initialise)
    
    def initialise(self):
        self.host = self.connect.entry_1.get()
        self.port = self.connect.entry_2.get()
        assert len(self.host) > 2
        assert int(self.port) > 1
        self.connect.destroy()
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.view = gui.View(self.parent)
        self.view.protocol('WM_DELETE_WINDOW', self.quit)
        self.view.Tabs.tab1.entry.bind('<Return>', self.send_command)
        # Set up the socket thread to do asynchronous I/O
        self.thread1 = threading.Thread(target=self.socket_thread)
        self.thread1.start()
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.refresh_queue()

    def refresh_queue(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.read_queue()
        self.parent.after(100, self.refresh_queue)
        
    def send_command(self, event):
            msg = self.view.Tabs.tab1.entry.get()
            self.view.Tabs.tab1.entry.selection_range(0, tkinter.END)
            self.socket.send(msg + '\n')
            self.input_queue.put(msg + '\n')
        
    def read_queue(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.input_queue.qsize():
            try:
                message = self.input_queue.get(0)
                self.view.Tabs.tab1.ansi_text.configure(state="normal")
                self.view.Tabs.tab1.ansi_text.write(message)
                self.view.Tabs.tab1.ansi_text.see(tkinter.END)
                self.view.Tabs.tab1.ansi_text.configure(state="disabled")
            except queue.Empty:
                pass

    def connect_socket(self):
        host = self.host
        port = int(self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)

        # connect to remote host
        self.socket.connect((host, port))
        self.running = True

    def socket_thread(self):
        self.connect_socket()
        while self.running:
            data = self.socket.recv(4096)
            if data:
                self.input_queue.put(data)
        
    def quit(self):
        self.running = False
        sys.exit()


if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
