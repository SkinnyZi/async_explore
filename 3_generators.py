# https://www.youtube.com/watch?v=MCs5OvhV9S4
# David Beazley - Python Concurrency From the Ground Up: LIVE! - PyCon 2015
import os
import socket
import logging

from helpers.constants import SERVER_ADDRESS, SERVER_PORT
from select import select

from helpers.utils import AddressRegister, address_to_str

READ = {}
WRITE = {}
TASKS = []

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(os.path.basename(__file__))


def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    logger.debug(f'Starting sever @ {SERVER_ADDRESS}:{SERVER_PORT}')

    while True:
        yield 'r', server_socket
        logger.debug('Waiting a first client...')
        client_socket, address = server_socket.accept()  # Blocking func
        address = address_to_str(address)

        logger.debug(f'New client {address}')
        AddressRegister.add_client(client_socket, address)

        TASKS.append(client(client_socket))


def client(client_socket):
    while True:
        yield 'r', client_socket
        request = client_socket.recv(4096)  # Blocking func | We may wait request from user too long
        logger.debug(f'{AddressRegister.get_client(client_socket)} < {request}')

        if not request:
            break
        else:
            response = b'pong\n'
            yield 'w', client_socket
            logger.debug(f'{AddressRegister.get_client(client_socket)} > {response}')
            client_socket.send(response)

    logger.debug(f'Disconnected {AddressRegister.get_client(client_socket)}')
    client_socket.close()


def event_loop():
    while any([TASKS, READ, WRITE]):
        while not TASKS:
            rlist, wlist, xlist = select(READ, WRITE, [])

            for sock in rlist:
                TASKS.append(READ.pop(sock))

            for sock in wlist:
                TASKS.append(WRITE.pop(sock))

        try:
            task = TASKS.pop(0)
            task_type, sock = next(task)

            if task_type == 'r':
                READ[sock] = task

            if task_type == 'w':
                WRITE[sock] = task

        except StopIteration:
            ...


if __name__ == '__main__':
    TASKS.append(server())
    try:
        event_loop()
    except KeyboardInterrupt:
        logger.debug('Shutting down the server...')

        for pending_tasks in TASKS:
            _, pending_socket = next(pending_tasks)
            pending_socket.close()

        for pending_socket, _ in {**READ, **WRITE}.items():
            pending_socket.close()
