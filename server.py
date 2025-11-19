import socket
import threading
import operator
import re
import queue
import time

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
class Thread:
    def __init__(self, handler, task_queue):
        self.stop_event = threading.Event()
        self.free_event = threading.Event()
        self.handler = handler
        self.tasks = task_queue
        self.thread = threading.Thread(target=self._worker, daemon=True)

    def start(self):
        self.thread.start()
        print(f'thread: {self.thread.name} started')

    def stop(self):
        self.stop_event.set()
        self.thread.join()

    def _worker(self):
        while not self.stop_event.is_set():
            try:
                self.free_event.set()
                task = self.tasks.get(True, timeout=0.5)
            except queue.Empty:
                continue

            self.free_event.clear()

            try:
                self.handler(task)
            finally:
                self.tasks.task_done()

        print(f"worker: {threading.current_thread().name} exit")
    

class ThreadPool:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[Thread pool] __exit__ stopping threads")
        for thread in self.threads:
            thread.stop()
        print(f"[Thread pool] __exit__ done")

    def __init__(self, handler, num: int = 5):
        self.threads = []
        self.handler = handler
        self.tasks = queue.Queue()
        self.add_threads(num)
        print(f"ThreadPool tasks queue id={id(self.tasks)}")

    def add_threads(self, num: int = 1):
        for _ in range(num):
            thread = Thread(self.handler, self.tasks)
            self.threads.append(thread)
            thread.start()

    def remove_threads(self, num: int = 2):
        # BUG: 1 : Done
        while len(self.threads) > 0 and num > 0:
            thread = self.threads[-1]
            if thread.free_event.is_set():
                # BUG: 2 : Done
                thread = self.threads.pop()
                thread.stop()
                num -= 1
            else:
                break
        print(f"lenth of thread pool: {len(self.threads)}")

    def submit(self, args):
        self.tasks.put(args)
    

def socket_calculator(conn: socket.socket):
    while True:
        data = (conn.recv(1024)).decode()
        if not data:
            break
        tid = threading.current_thread().name
        print(f'tid={tid} data={data}')
        ret = eval(data)
        conn.sendall(str(ret).encode())
    conn.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8080))
server.listen(5)

pool1 = ThreadPool(socket_calculator, 5)
pool2 = ThreadPool(socket_calculator, 3)
while True:
    try:
        conn, _ = server.accept()
        print('server received data')
        pool1.submit(conn)
        pool2.submit(conn)
        # thread_pool.add_threads(1)
    except KeyboardInterrupt:
        break
pool1.remove_threads(3)
server.close()
