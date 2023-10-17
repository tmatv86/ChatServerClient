import socket, threading
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
        self.stop_falg = False

    def binding(self):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen(10)
        self.lsock.setblocking(False)  # non-blocking sockets
        self.sockets.append(self.lsock)
        # print("Socket is in: ", self.sockets)
        print(f"Listening on host and port: {(self.host, self.port)}")

    def start_server(self):
        global num_of_clients
        logging.info(f'{datetime.datetime.now()}: Waiting for connections...')
        while not self.stop_falg:
            rread, rwrite, err = select.select(self.sockets, [], [], 0)
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

                        if 'exit' in data.decode():
                            self.remove_user(users, sock)

                        if data:
                            for s in self.sockets:
                                if s != self.lsock and s != sock:
                                    s.send(data)
                        else:
                            self.remove_user(users, sock)
                    except:
                        print("Error in client socket: ")
                        traceback.print_exc()

    def remove_user(self, users, conn):
        keyval = None
        for k, v in users.items():
            if conn in v:
                keyval = k
        if keyval:
            del users[keyval]
            logging.info(f'{datetime.datetime.now()}: Connection found! User exited: {v[1]}')

        if conn in self.sockets:
            print('C == CONN')
            conn.close()
            self.sockets.remove(conn)

    def close_server(self):
        #try:
        for s in self.sockets:
            self.sockets.remove(s)
        print('Remove all sockets...', self.sockets)
        users.clear()
        print('Clean up users: ', users)
        threading.active_count()
        sys.exit(5)
        #except AttributeError:
        #    print('Server forcibly close... ')
        #    traceback.print_exc()
        #    sys.exit(1)
class ServerManagerThrd(threading.Thread):

    command = ''
    def __init__(self, server_socket:ServerSocket):
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.thr_stopping = False
    def run(self):
        commands = ['quit', 'kick', 'listusers']
        while not self.thr_stopping:
            command = input("You can input command to manage server\n")
            if command not in commands:
                print('Unknown option: \'', command, '\'')
            if command == 'listusers':
                for k, v in users.items():
                    print('User id: ', k, 'name: ', v[1], ' params: ', v[0])

            elif (command == 'quit'):
                self.thr_stopping = True
                self.server_socket.stop_falg = True
                self.server_socket.close_server()

            elif command == 'kick':
                u = input('Input user to kick: ')
                if not u:
                    print('No such user or username is empty!')
                else:
                    logger.info(f'{u} will be disconnected from the server by admin')
                    val = None
                    for k, v in users.items():
                        if u in v:
                            val = v[0]
                    self.server_socket.remove_user(users, val)

# main method
if __name__ == "__main__":

    print(threading.active_count())

    # server thread manager
    server = ServerSocket(socket, PORT)
    manageth = ServerManagerThrd(server)
    manageth.start()

    server = ServerSocket("localhost", 65534)
    server.binding()
    server.start_server()

    sys.exit(server)