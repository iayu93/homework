import socket
import json

for _ in range(3):
    for i in range(2):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(('127.0.0.1', 8080))
        row_data = {'handler': 'calculator', 'data': '1+1'}
        client.send(json.dumps(row_data).encode())
        data = client.recv(1024)
        print("server replied: ", data.decode())
        client.close()
    for i in range(1):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)
        client.connect(('127.0.0.1', 8080))
        row_data = {'handler': 'to_lower', 'data': 'YJ'}
        client.send(json.dumps(row_data).encode())
        data = client.recv(1024)
        print("server replied: ", data.decode())
        client.close()