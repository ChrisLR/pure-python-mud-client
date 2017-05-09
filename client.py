import sys
import threading
import queue
import socket
import tkinter
import gui
import telnet.parser


class Controller(object):
    def __init__(self, parent):
        self.host = None
        self.port = None
        self.input_queue = None
        self.output_queue = None
        self.trigger_queue = None
        self.view = None
        self.running = False
        self.thread1 = None
        self.thread2 = None
        self.socket = None
        self.telnet_parser = None
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
        self.trigger_queue = queue.Queue()
        self.view = gui.View(self.parent)
        self.view.protocol('WM_DELETE_WINDOW', self.quit)
        self.view.Tabs.tab1.entry.bind('<Return>', self.send_command)
        # Set up the socket thread to do asynchronous I/O
        self.thread1 = threading.Thread(target=self.socket_thread)
        self.thread1.start()
        self.thread2 = threading.Thread(target=self.trigger_thread)
        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.refresh_queue()

    def refresh_queue(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.read_from_queue()
        self.parent.after(100, self.refresh_queue)
        
    def send_command(self, event):
            msg = self.view.Tabs.tab1.entry.get()
            self.view.Tabs.tab1.entry.selection_range(0, tkinter.END)
            encoded_message = (msg + '\n').encode('utf-8')
            self.socket.send(encoded_message)
            # TODO Input Queue must differentiate between a server message and an echo message.
            # self.input_queue.put(encoded_message)

    def read_from_queue(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.input_queue.qsize():
            try:
                message = self.input_queue.get(0)
                self.view.Tabs.tab1.ansi_text.configure(state="normal")
                colorless_message = self.view.Tabs.tab1.ansi_text.write(message)
                self.trigger_queue.put(colorless_message)
                self.view.Tabs.tab1.ansi_text.see(tkinter.END)
                self.view.Tabs.tab1.ansi_text.configure(state="disabled")
            except queue.Empty:
                pass

    def connect_socket(self):
        host = self.host
        port = int(self.port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(120)
        self.telnet_parser = telnet.parser.TelnetParser(self.socket, self.input_queue, self.output_queue)

        # connect to remote host
        self.socket.connect((host, port))
        self.running = True
        self.thread2.start()

    def socket_thread(self):
        self.connect_socket()
        while self.running:
            data = self.socket.recv(4096)
            telnet_messages = list()
            parsed_data = self.telnet_parser.handle_and_remove_telnet_bytes(data, len(data), telnet_messages)
            if parsed_data:
                self.input_queue.put(parsed_data)
            if not parsed_data:
                self.input_queue.put('Disconnected.\n'.encode('utf-8'))
                self.quit()

    def trigger_thread(self):
        while self.running:
            try:
                message = self.trigger_queue.get(0)
                if "You finish" in message:
                    print("OH YEAH")
            except:
                pass
        
    def quit(self):
        self.running = False
        sys.exit()


if __name__ == '__main__':
    root = tkinter.Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()
