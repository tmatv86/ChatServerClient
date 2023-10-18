import socket
import sys
import select

def main():

    HOST = "127.0.0.1"
    PORT = 65534
    nickname = input('Please, input nickname: ')

    # creating client socket & thread
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
    except:
        print('Unable to connect to socket!')
        sys.exit(1)

    message = nickname + ' has just connected!'
    client.send(message.encode())

    sockets = [sys.stdin, client]

    while True:
        rread, rwrite, err = select.select(sockets, [], [], 0)
        for sock in rread:
            if sock == client:
                data = sock.recv(4096)
                if data:
                    print(data.decode())
                else:
                    sys.exit(1)
            else:
                message_to_send = input('')
                if message_to_send == 'exit.':
                    client.send(f'{nickname} has been disconnected!'.encode())
                    client.close()
                    sockets.remove(client)
                    sys.exit(2)
                client.send((f'{nickname}: {message_to_send}').encode())
                print(nickname+ f': {message_to_send}')

if __name__ == '__main__':
    sys.exit(main())

