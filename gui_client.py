
import threading
import sys
import Queue
import select
import socket
from Tkinter import *
from gui import Connector, View


class Controller(object):
    def __init__(self, parent):
        self.parent = parent
        
        
        #connection window
        self.connect = Connector(root)
        self.connect.button.config(command=self.initialise)

    
    def initialise(self):
        self.host = self.connect.e1.get()
        self.port = self.connect.e2.get()
        try:
            assert len(self.host) > 2
            assert int(self.port) > 1
            self.connect.destroy()
            self.readQueue = Queue.Queue()
            self.writeQueue = Queue.Queue()
            self.view = View(self.parent)
            self.view.protocol('WM_DELETE_WINDOW', self.quit)
            self.view.Tabs.tab1.E.bind('<Return>', self.sendCommand)
            # Set up the socket thread to do asynchronous I/O
            self.running = 1
            self.thread1 = threading.Thread(target=self.socketThread)
            self.thread1.start()
            # Start the periodic call in the GUI to check if the queue contains
            # anything
            self.periodicCall()
        except AssertionError:
            pass
            


    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        self.recieveQueue()
        self.parent.after(100, self.periodicCall)
        
    def sendCommand(self, event):
            msg = self.view.Tabs.tab1.E.get()
            self.view.Tabs.tab1.E.selection_range(0, END) 
            self.s.send(msg+'\n')
            #~ print 'msg sent'
            self.readQueue.put(msg+'\n')
        
    def recieveQueue(self):
        """
        Handle all the messages currently in the queue (if any).
        """
        while self.readQueue.qsize():
            try:
                msg = self.readQueue.get(0)
                self.view.Tabs.tab1.T.configure(state="normal")
                self.view.Tabs.tab1.T.write(msg)
                self.view.Tabs.tab1.T.see(END)
                self.view.Tabs.tab1.T.configure(state="disabled")
                with open('msg.log', 'a') as f:
                    f.write(msg+'\n')
                    f.close()
            except Queue.Empty:
                pass
            
    def socketThread(self):
        host = self.host
        port = int(self.port)
         
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        self.s = s
         
        # connect to remote host
        #~ try :
        s.connect((host, port))
        #~ except :
            #~ print 'Unable to connect'
            #~ sys.exit()
            
        while self.running:
            socket_list = [s]
         
            # Get the list sockets which are readable
            read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
            for sock in read_sockets:
                #incoming message from remote server
                if sock == s:
                    data = sock.recv(4096)
                    if not data :
                        print '\nDisconnected from server'
                        self.quit()
                    else :
                        self.readQueue.put(data)

        
    def quit(self):
        self.running = 0
        sys.exit()


if __name__ == '__main__':
    root = Tk()
    root.withdraw()
    app = Controller(root)
    root.mainloop()