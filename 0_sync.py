import os
import socket
import logging

from helpers.constants import SERVER_PORT, SERVER_ADDRESS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(__file__))

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
server_socket.listen()

while True:
    logger.debug('Waiting a client...')
    client_socket, address = server_socket.accept()  # Blocking func
    logger.debug(f'Connection form {address}')

    while True:
        logger.debug('Inner loop | recv() & send()')
        request = client_socket.recv(4096)  # Blocking func | We may wait request from user too long

        if not request:
            break
        else:
            response = b'pong\n'
            client_socket.send(response)

    logger.debug('Out of inner loop. close() connection with client')
    client_socket.close()
