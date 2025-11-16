import socket
import threading
import operator
import re
import queue

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

class ThreadPool:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for thread in self.threads:
            thread.join()

    def __init__(self, num: int = 5):
        self.threads = []
        self.tasks = queue.Queue()
        self._add_threads(num)

    def runner(self):
        while True:
            try:
                task = self.tasks.get()
                self.handler(task)
            finally:
                self.tasks.task_done()

    def _add_threads(self, num: int = 1):
        for _ in range(num):
            thread = threading.Thread(target=self.runner, daemon=True).start()
            self.threads.append(thread)

    def add_threads(self, num: int = 1):
        self._add_threads(num)

    def submit(self, handler, args):
        self.handler = handler
        self.tasks.put(args)

def socket_calculator(conn: socket.socket):
    data = (conn.recv(1024)).decode()
    if not data:
        return
    tid = threading.current_thread().name
    print(f'tid={tid} data={data}')
    ret = eval(data)
    conn.sendall(str(ret).encode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8080))
server.listen(5)


while True:
    try:
        with ThreadPool(5) as thread_pool:
            conn, _ = server.accept()
            print('server received data')
            thread_pool.submit(socket_calculator, conn)
    except KeyboardInterrupt:
        break
server.close()
