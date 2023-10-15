import sys, socket, threading
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMainWindow, QWidget, QPlainTextEdit, QPushButton, QVBoxLayout, QLineEdit, QApplication
from PyQt6.QtCore import QSize



class ClientSocket():

    client = 0
    client_thrd = None
    stop_thread = False

    def __init__(self):
        self.HOST = "127.0.0.1"
        self.PORT = 65531
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.HOST, self.PORT))

    def read_from_socket(self):
        while 1:
            if self.stop_thread:
                break
            try:
                from_server = self.client.recv(4096).decode()
                if from_server:
                    mainWin.text_area.insertPlainText(from_server+'\n')
            except:
                self.client.close()
                sys.exit(2)

class ExampleWindow(QMainWindow):


    client_socket = None
    nickname = "GraPH"

    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("")
        layout = QVBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # add text files
        self.text_field = QLineEdit()
        self.setMinimumSize(QSize(740, 490))
        self.setWindowTitle("Chat Window")

        # Add text area
        self.text_area = QPlainTextEdit(self)
        self.text_area.move(10, 10)
        layout.addWidget(self.text_area)
        layout.addWidget(self.text_field)


        # add buttons on the widget
        button = QPushButton("Connect")
        button.clicked.connect(self.connect)
        layout.addWidget(button)

        button = QPushButton("Send message")
        button.clicked.connect(self.send_message)
        layout.addWidget(button)

        button = QPushButton("Exit", self)
        button.clicked.connect(self.exit_chat)
        layout.addWidget(button)

    def connect(self):
        print('Connect to server...')
        try:
            self.client_socket = ClientSocket('127.0.0.1', 65531)
            self.thrdClient = threading.Thread(target=self.client_socket.read_from_socket)
            self.thrdClient.start()
            print('Connection established successfully!')
        except:
            print('Unable to connect...')

    def send_message(self, client_socket=None):
        string_to_send = self.nickname + ": " + self.text_field.text()
        self.text_field.clear()
        print(string_to_send)
        try:
            self.client_socket.client.send(string_to_send.encode())
        except socket.error:
            print('Unable to send message: ', socket.error)

    def exit_chat(self):
        print('Exiting chat')
        try:
            self.send_message('Client disconnected!')
            self.client_socket.client.close()
            sys.exit(app.exec())
        except Exception:
            print('Unable to properly shutdown socket: ', socket.error, ' not connected?')
            sys.exit(1)
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit(app.exec())

