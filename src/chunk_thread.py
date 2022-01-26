from threading import Thread

# Thread with return value code taken from
# https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
# Thank you for the incredible answer!

class ChunkThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group=group, target=target, name=name, args=args, kwargs=kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return