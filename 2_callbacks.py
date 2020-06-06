import os
import socket
import logging
import selectors

from helpers.constants import SERVER_ADDRESS, SERVER_PORT
from helpers.utils import AddressRegister, address_to_str

SELECTOR = selectors.DefaultSelector()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(__file__))


def server_setup():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    logger.debug(f'Starting sever @ {SERVER_ADDRESS}:{SERVER_PORT}')

    SELECTOR.register(server_socket, selectors.EVENT_READ, accept_connection)


def accept_connection(server_socket_):
    client_socket, address = server_socket_.accept()  # Blocking func
    address = address_to_str(address)

    SELECTOR.register(client_socket, selectors.EVENT_READ, send_response)
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

        SELECTOR.unregister(client_socket)
        AddressRegister.delete_client(client_socket)
        client_socket.close()


def event_loop():
    logger.debug('Waiting a first client...')

    while True:
        try:
            events = SELECTOR.select()

            for key, event_bit_mask in events:
                callback = key.data
                callback(key.fileobj)

        except KeyboardInterrupt:
            break

    logger.debug('Shutting down the server...')


if __name__ == '__main__':
    server_setup()
    event_loop()
