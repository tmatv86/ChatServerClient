import socket
import select
import traceback
import datetime, logging
import sys

users = {}

# logger format
logger = logging.getLogger()
logging.basicConfig(filename="chat_server.log", level=logging.DEBUG)
logging.info(f'{datetime.datetime.now()}: Chat server started main AChatServer.py')
logging.info(f'{datetime.datetime.now()}: Debug level: logger.debug')
logging.info(f'{datetime.datetime.now()}:......................................')

HOST = '127.0.0.1'
PORT = 65534

BUFSIZE = 4096
num_of_clients = 0

class ServerSocket:

    socket = None
    sockets = []
    lsock = None
    welcome_string = " has joined chat!"

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()

    def binding(self):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen(10)
        self.lsock.setblocking(False)  # non-blocking sockets
        self.sockets.append(self.lsock)
        # print("Socket is in: ", self.sockets)
        print(f"Listening on host and port: {(self.host, self.port)}")

    def start_server(self):
        global num_of_clients
        while True:
            logging.info(f'{datetime.datetime.now()}: Waiting for connections...')
            rread, rwrite, err = select.select(self.sockets, self.sockets, [])
            for sock in rread:
                if sock == self.lsock:
                    conn, addr = self.lsock.accept()
                    conn.setblocking(False)
                    self.sockets.append(conn)
                    logging.info(f'{datetime.datetime.now()}: New connection from client: {addr}')
                    num_of_clients = num_of_clients + 1
                    users[num_of_clients] = [conn]
                else:
                    try:
                        data = sock.recv(BUFSIZE)
                        print("Server received: " + data.decode())

                        if 'has just connected' in data.decode():
                            user = data.decode().split(' ')[0]
                            users.get(list(users)[-1]).append(user)

                        if data:
                            for s in self.sockets:
                                if s != self.lsock and s != sock:
                                    s.send(data)
                        else:
                            if sock in self.sockets:
                                self.sockets.remove(sock)
                                keyval = None
                                for k,v in users.items():
                                    if sock in v:
                                        print('Connection found! User exited: ', v[1])
                                        keyval = k
                                if not keyval:
                                    del users[keyval]
                    except:
                        print("Error in clinet socket: ")
                        traceback.print_exc()


# main method
if __name__ == "__main__":
    server = ServerSocket("localhost", 65534)
    server.binding()
    server.start_server()