import socket
import sys
import threading

def main():

    HOST = "127.0.0.1"
    PORT = 65531

    nickname = input('Please, input nickname: ')

    def read_socket():
        while 1:
            try:
                from_server = client.recv(4096).decode()
                if from_server:
                    print(from_server)
            except Exception:
                client.close()
                break

    # creating client socket & thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    thrdClient = threading.Thread(target=read_socket)
    thrdClient.start()

    client.send(f'{nickname} has just connected!'.encode())

    while True:
        string = input("")
        str = f"{nickname}: " + string
        client.send(str.encode())
        if string == 'exit':
            client.close()
            sys.exit(0)

if __name__ == '__main__':
    main()
