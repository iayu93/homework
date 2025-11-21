import socket
import threading
import operator
import re
import queue
import time
import json

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

def calculator(conn: socket.socket, expr: str):
    print(f"calculating {expr}")
    ret = eval(expr)
    conn.sendall(str(ret).encode())

def to_lower(conn: socket.socket, data: str):
    conn.sendall(data.lower().encode())

HANDLERS = {
    'calculator': calculator,
    'to_lower': to_lower
}

class Thread:
    def __init__(self, task_queue):
        self.stop_event = threading.Event()
        self.free_event = threading.Event()
        self.tasks = task_queue
        self.thread = threading.Thread(target=self._worker, daemon=True)

    def start(self):
        self.thread.start()
        print(f'thread: {self.thread.name} started')

    def stop(self, wait: bool = True):
        self.stop_event.set()
        if wait:
            self.thread.join()

    def _worker(self):
        print(f"worker is running, {threading.current_thread().name}")
        while not self.stop_event.is_set():
            try:
                self.free_event.set()
                task = self.tasks.get(True, timeout=0.5)
                print(f"task: {task}")
            except queue.Empty:
                continue

            self.free_event.clear()

            conn, to_handle = task
            print(f"to handle: {to_handle}")
            to_handle = json.loads(to_handle) 
            handler = to_handle['handler']
            data = to_handle['data'] 
            try:
                HANDLERS[handler](conn, data)
            finally:
                self.tasks.task_done()

        print(f"worker: {threading.current_thread().name} exit")
    
class ThreadPool:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[Thread pool] __exit__ stopping threads")
        self.shutdown(wait=True)
        print(f"[Thread pool] __exit__ done")

    def __init__(self, num: int = 5):
        self.threads = []
        self.tasks = queue.Queue()
        self.accepting = True
        self.add_threads(num)
        print(f"ThreadPool tasks queue id={id(self.tasks)}")

    def add_threads(self, num: int = 1):
        for _ in range(num):
            thread = Thread(self.tasks)
            self.threads.append(thread)
            thread.start()

    def remove_threads(self, num: int = 2):
        # BUG: 1 : Done
        removed = 0
        for thread in list(self.threads):
            if removed >= num:
                break
            if thread.free_event.is_set():
                self.threads.remove(thread)
                thread.stop()
                removed += 1
        print(f"lenth of thread pool: {len(self.threads)}")
        return removed

    def shutdown(self, wait: bool = False):
        self.accepting = False
        if wait:
            self.tasks.join()
        for thread in self.threads:
            thread.stop(wait)

    def submit(self, *args):
        if not self.accepting:
            raise RuntimeError("ThreadPool is shutting down, cannot submit new tasks")
        self.tasks.put(args)

def handle_connection(conn: socket.socket, pool: ThreadPool):
    try:
        while True:
            data = conn.recv(2048).decode()
            if not data:
                break
            tid = threading.current_thread().name
            pool.submit(conn, data)
            print(f'tid={tid} data={data}')
            # time.sleep(3)
    finally:
        conn.close()

class YjProc:
    def __init__(self, handler: callable, data: str, sock: socket.socket = None):
        self.handler = handler
        self.data = data
    def set_sock(self, sock):
        self.sock = sock
    def get_sock(self):
        return self.sock

sock_map = {}

def register_sock(sock):
    sock_map[id(sock)] = sock

def get_sock(obj_id):
    return sock_map.get(obj_id)

def accept_loop(server: socket.socket, pool: ThreadPool):
    sock_queue = queue.Queue()
    while True:
        try:
            conn, _ = server.accept()
            print('server received data')
            register_sock(conn)
            sock_queue.put(get_sock(conn))
            # threading.Thread(target=handle_connection, args=(conn, pool), daemon=True).start()
            try:
                while True:
                    data = conn.recv(2048).decode()
                    if not data:
                        break
                    yjdata: YjProc = json.loads(data)
                    yjdata.set_sock(get_sock(conn))
                    pool.submit(yjdata)
                    tid = threading.current_thread().name
                    print(f'tid={tid} data={data}')
            finally: conn.close()
                
            # pool2.submit(conn)
            # thread_pool.add_threads(1)
        except KeyboardInterrupt:
            break



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8080))
server.listen(5)

pool1 = ThreadPool(3)
accept_loop(server, pool1)
pool1.remove_threads(3)
server.close()
