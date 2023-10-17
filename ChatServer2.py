import socket
import threading
import sys
import logging, datetime

threads = []
users = {}

# logger format
logger = logging.getLogger()
logging.basicConfig(filename="chat_server.log", level=logging.DEBUG)
logging.info(f'{datetime.datetime.now()}: Chat server started main ChatServer.py')
logging.info(f'{datetime.datetime.now()}: Debug level: logger.debug')
logging.info(f'{datetime.datetime.now()}:......................................')

class ServerSocket:

    global i  # number of users
    server_socket = None
    host = "127.0.0.1"
    welcome_string = " has joined chat!"

    def __init__(self, socket, threads):
        self.server_socket = socket.socket()
        self.host = "localhost"

    def start_server(self, port):
        self.server_socket.bind((self.host, port))
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.listen()
        i = 0

        while True:
            try:
                logging.info(f'{datetime.datetime.now()}: Waiting for connections...')
                conn, addr = self.server_socket.accept()
                logging.info(f'{datetime.datetime.now()}: New connection from client: ')
                i = i + 1
                users[i] = [conn]
                thrd = ThreadSocket(conn, threads, self.server_socket, addr)
                users.get(i).append(thrd)
                threads.append(thrd)
                thrd.start()
            except OSError:
                self.server_socket.close()
                logging.info(f'{datetime.datetime.now()}: Socket closed by the server')
                sys.exit(2)
            except KeyboardInterrupt:
                sig_kill_handler()
                break

    def server_close(self):
        try:
            self.server_socket.close()
        except OSError:
            logging.info(f'{datetime.datetime.now()}: ERROR: Unable to close server socket')
class ThreadSocket(threading.Thread):
    global addr

    def __init__(self, connection, threads, server_socket, addr):
        threading.Thread.__init__(self)
        self.exitflag = False
        self.connection = connection
        self.shutdown_flag = threading.Event()
        self.serverSocket = server_socket
        self.addr = addr

    def run(self):

        while True:
            if self.exitflag:
                break
            try:
                string_data = ''
                data = self.connection.recv(4096)
                if not data: break
                string_data = string_data + data.decode()
                if 'has just connected' in string_data:
                    user = string_data.split(' ')[0]
                    users.get(list(users)[-1]).append(user)
                    logging.info(f'{users.get(list(users)[-1])} is now in the chat')
                if 'exit' in string_data:
                    threads.remove(self.get_thread())
                    keyval = None
                    for k, v in users.items():
                        if self.get_thread() in v:
                            v[0].close()
                            v[1].exitflag = True
                            keyval = k
                    del users[keyval]
                    logging.info(f'{datetime.datetime.now()}: client disconnected...')
                else:
                    for thrd in threads:
                        thrd.__send_all__(thrd, string_data)
            except Exception:
                logging.info(f'{datetime.datetime.now()}: traceback.format_exc()')
                logging.info(f'{datetime.datetime.now()}: Client disconnected')
                self.connection.close()
            except KeyboardInterrupt:
                sig_kill_handler()
                break

    def __send_all__(self, th, string_data):
        # send message to all connected clients
        th.get_connection().send((string_data).encode())

    def get_connection(self):
        return self.connection

    def get_thread(self):
        return self

# Manage server
class ServerManagerThrd(threading.Thread):

    command = ''
    thr_stopping = False
    def __init__(self, server_socket:ServerSocket, stop_event):
        threading.Thread.__init__(self)
        self.server_socket = server_socket
        self.stop_event = stop_event

    def run(self):
        commands = ['quit', 'kick', 'listusers']
        while not self.stop_event.is_set():
            command = input("You can input command to manage server\n")
            if command not in commands:
                print('Unknown option: \'', command, '\'')
            if command == 'listusers':
                for k, v in users.items():
                    print('User id: ', k, 'name: ', v[2], ' params: ', v[0], ',', v[1])

            if (command == "quit"):
                for th in threads:
                    th.exitflag = True
                self.server_socket.server_close()
                self.stop_event.set() 
                sys.exit(4)
            if 'kick' in command:
                u = input('Input user to kick: ')
                if not u:
                    print('No such user or username is empty!')
                else:
                    logger.info(f'{u} will be disconnected from the server by admin')
                    keyval = None
                    for k, v in users.items():
                        if u in v:
                            print('User found: ', u, 'key: ', k)
                            print('Socket: ', v[0])
                            try:
                                v[0].close()
                                v[1].exitflag = True
                                threads.remove(v[1].get_thread())
                                keyval = k
                            except Exception:
                                print('Unable to close socket!')
                    del users[keyval]

def sig_kill_handler():
    # all threads interrupting
    logging.info(f'{datetime.datetime.now()}: Interrupted from the keyboard')
    sys.exit(3)

if __name__ == '__main__':

    stop_event = threading.Event()

    server = ServerSocket(socket, threads)
    manageth = ServerManagerThrd(server, stop_event)

    manageth.start()
    server.start_server(65531)

    stop_event.set()
    manageth.join()







