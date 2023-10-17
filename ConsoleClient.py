import socket
import sys
import threading

def main():

    HOST = "127.0.0.1"
    PORT = 65534

    nickname = input('Please, input nickname: ')

    def read_socket():
        while True:
            if exitflag:
                break
            try:
                from_server = client.recv(4096).decode()
                if from_server:
                    print(from_server)
            except Exception:
                client.close()
                sys.exit(2)

    # creating client socket & thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    exitflag = False
    thrdClient = threading.Thread(target=read_socket)
    thrdClient.start()

    client.send(f'{nickname} has just connected!'.encode())

    while True:
        try:
            string = input("")
            str1 = f"{nickname}: " + string
            print(str1)
            client.send(str1.encode())
            if string == 'exit':
                exitflag = True
                client.close()
                sys.exit(0)
        except Exception:
            print('Server disconnected...')
            exitflag = True
            client.close()
            sys.exit(1)


if __name__ == '__main__':
    main()
