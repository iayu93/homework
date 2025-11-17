import socket

for i in range(2):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(5)
    client.connect(('127.0.0.1', 8080))
    client.send((f"1+1").encode())
    data = client.recv(1024)
    print("server replied: ", data.decode())
    client.close()