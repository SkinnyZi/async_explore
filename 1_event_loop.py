import logging
import os
import socket
from select import select

from helpers.constants import SERVER_ADDRESS, SERVER_PORT
from helpers.utils import AddressRegister, address_to_str

READ_MONITOR = []

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(__file__))

# Setup server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
server_socket.listen()
logger.debug(f'Starting sever @ {SERVER_ADDRESS}:{SERVER_PORT}')


def accept_connection(server_socket_):
    client_socket, address = server_socket_.accept()  # Blocking func
    address = address_to_str(address)

    READ_MONITOR.append(client_socket)
    AddressRegister.add_client(client_socket, address)

    logger.debug(f'New client {address}')


def send_response(client_socket):
    request = client_socket.recv(1024)  # Blocking func | We may wait request from user too long

    if request:
        logger.debug(f'{AddressRegister.get_client(client_socket)} < {request}')

        response = b'pong\n'
        client_socket.send(response)

        logger.debug(f'{AddressRegister.get_client(client_socket)} > {response}')

    else:
        logger.debug(f'Disconnected {AddressRegister.get_client(client_socket)}')

        AddressRegister.delete_client(client_socket)
        client_socket.close()
        READ_MONITOR.remove(client_socket)


def event_loop():
    logger.debug('Waiting a first client...')

    while True:
        try:
            rlist, wlist, xlist = select(READ_MONITOR, [], [])

            for sock in rlist:
                if sock is server_socket:
                    accept_connection(sock)
                else:
                    send_response(sock)
        except KeyboardInterrupt:
            break

    logger.debug('Shutting down the server...')


if __name__ == '__main__':
    READ_MONITOR.append(server_socket)
    event_loop()
