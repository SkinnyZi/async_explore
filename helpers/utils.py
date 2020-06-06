import socket


class AddressRegister:
    ADDRESS_REGISTRY = {}

    @classmethod
    def add_client(cls, client: socket, address: str):
        cls.ADDRESS_REGISTRY.update({client.fileno(): address})

    @classmethod
    def get_client(cls, client):
        return cls.ADDRESS_REGISTRY.get(client.fileno())

    @classmethod
    def delete_client(cls, client):
        cls.ADDRESS_REGISTRY.pop(client.fileno())


def address_to_str(address):
    return ":".join(list(map(str, address)))

