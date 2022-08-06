import time

def timer(func, *args):
    start = time.time()
    func(*args)
    return time.time() - start