import socket
import threading
import operator
import re
import queue

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8080))
server.listen(5)

'''
线程池
固定线程数量
闲线程列表
忙线程列表

如果有任务，则去闲线程找，没有则阻塞
忙线程结束后归入闲线程

复用时线程内容如何动态获取任务内容
共享空间或者消息队列

长期没有任务时如何处理线程，避免长时占用cpu
挂起/停掉，来任务后再创建
'''

tasks = queue.Queue()

def worker():
    while True:
        try:
            conn = tasks.get()
            data = (conn.recv(1024)).decode()
            conn.sendall(str(eval(data)).encode())
            conn.close()
        finally:
            tasks.task_done()
    
def new_threads(num: int = 5):
    for _ in range(num):
        threading.Thread(target=worker, daemon=True).start()


new_threads()
while True:
    try:
        conn = server.accept()
        print('server received data')
        tasks.put(conn)
    except KeyboardInterrupt:
        break
server.close()
