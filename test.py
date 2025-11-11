import operator
import threading
import time

ops = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv
}

def calulator(num1, num2, operator:str):
    return ops[operator](num1, num2)

start = time.time()
threads = [threading.Thread(target=calulator, args=(i, i+1, '+')) for i in range(100000)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("耗时: ", time.time() - start)

start = time.time()
for i in range(100000):
    pass
print("耗时: ", time.time() - start)

start = time.time()
results = [calulator(i, i+1, '+') for i in range(100000)]
print("耗时: ", time.time() - start)

start = time.time()
results = (calulator(i, i+1, '+') for i in range(100000))
for r in results:
    pass
print("耗时: ", time.time() - start)