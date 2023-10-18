import socket, threading
import select
import traceback
import datetime, logging
import sys, signal

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
    server_socket = None
    welcome_string = " has joined chat!"

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket()
        self.stop_falg = False
        signal.signal(signal.SIGINT, self.close_server)

    def binding(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(10)
        self.sockets.append(self.server_socket)
        self.server_socket.setblocking(False)  # non-blocking sockets
        print(f"Listening on host and port: {(self.host, self.port)}")


    def start_server(self):
        global num_of_clients
        logging.info(f'{datetime.datetime.now()}: Waiting for connections...')

        while not self.stop_falg:
            rread, rwrite, err = select.select(self.sockets, [], [], 0)
            for sock in rread:
                if sock == self.server_socket:
                    conn, addr = self.server_socket.accept()
                    conn.setblocking(False)
                    self.sockets.append(conn)
                    logging.info(f'{datetime.datetime.now()}: New connection from client: {addr}')
                    num_of_clients = num_of_clients + 1
                    users[num_of_clients] = [conn]
                else:
                    try:
                        data = sock.recv(BUFSIZE)
                        if 'has just connected' in data.decode():
                            user = data.decode().split(' ')[0]
                            users.get(list(users)[-1]).append(user)

                        if 'exit.' in data.decode():
                            self.remove_user(users, sock)
                        if data:
                            for s in self.sockets:
                                if s != self.server_socket and s != sock:
                                    s.send(data)
                        else:
                            self.remove_user(users, s)

                    except:
                        print("Error in client socket: ")
                        traceback.print_exc()

        #self.server_socket.close()
    def remove_user(self, users, conn):

        keyval = None
        for k, v in users.items():
            if conn in v:
                keyval = k
        if keyval:
            del users[keyval]
            logging.info(f'{datetime.datetime.now()}: Connection found! User exited: {v[1]}')
        if conn:
            conn.close()
        self.sockets.remove(conn)

    def close_server(self, signum, frame):
        print('Remove all sockets...', self.sockets)
        for s in self.sockets:
            s.close()
            self.sockets.remove(s)
        if self.server_socket:
            self.server_socket.close()
        #users.clear()
        print('Clean up users: ', users)


class ServerManagerThrd(threading.Thread):

    command = ''
    def __init__(self, server_socket:ServerSocket):
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.thr_stopping = False
    def run(self):
        commands = ['quit', 'kick', 'userlist']
        while not self.thr_stopping:
            command = input("You can input command to manage server\n")
            if command not in commands:
                print('Unknown option: \'', command, '\'')
            if 'userlist' in command:
                for k, v in users.items():
                    print('User id: ', k, 'name: ', v[1], ' params: ', v[0])

            elif command == 'quit':
                #self.thr_stopping = True
                self.server_socket.stop_falg = True
                print(self.server_socket.stop_falg)
                break

            elif command == 'kick':
                u = input('Input user to kick: ')
                if not u:
                    print('No such user or username is empty!')
                else:
                    logger.info(f'{datetime.datetime.now()}: \'{u}\' will be disconnected from the server by admin')
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