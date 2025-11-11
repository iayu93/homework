import socket
import threading
import operator
import re

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8080))
server.listen(5)

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def calulator(num1, num2, operator:str, ret):
    ret['value'] = ops[operator](num1, num2)

try:
    while True:
        print("Waiting for client's connect...")
        conn, addr = server.accept()
        print("connected", addr)
        exps = []
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                data = data.decode()
                print("client send:", data)
                m = re.fullmatch(r"\s*(\d+)\s*([+\-*/]\s*)", data)
                if not m:
                    conn.sendall(b"invalid expression\n")
                    break
                num1, op, num2 = m.groups()
                conn.send(b"I received the data")
        finally:
            conn.close()
        ret = {}
        thread = threading.Thread(target=calulator, args=(num1, op, num2, ret))
        conn.send((f"The caculated result is: {ret['value']}").encode())
        thread.start()
        thread.join()
except KeyboardInterrupt:
    print("shutting down")
finally:
    server.close()