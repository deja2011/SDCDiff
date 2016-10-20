"""A single process module to differentiate two cmd pools store their differences."""

__author__ = 'Lawrence Li'
__version__ = '2.0'
__date__ = 'Fri Feb 27 2015'


import subprocess, threading


class Comparator(threading.Thread):

    def __init__(self, pool_1, pool_2, lock_1, lock_2, all_done):
        threading.Thread.__init__(self)
        self.pool_1 = pool_1
        self.pool_2 = pool_2
        self.lock_1 = lock_1
        self.lock_2 = lock_2
        self.all_done = all_done


    def run(self):
        prevlen_1, prevlen_2 = 0, 0
        while True:
            if len(self.pool_1) > prevlen_1 or len(self.pool_2) > prevlen_2:
                self.lock_1.acquire()
                if self.lock_2.acquire(False):
                    # Now both lock_1 and lock_2 are acquired successfully.
                    intersect = self.pool_1 & self.pool_2
                    if intersect:
                        self.pool_1 -= intersect
                        self.pool_2 -= intersect
                    prevlen_1 = len(self.pool_1)
                    prevlen_2 = len(self.pool_2)
                    self.lock_2.release()
                    self.lock_1.release()
                else:
                    # Failed to acquire lock_2. Need to release lock_1 immediately.
                    self.lock_1.release()
            elif self.all_done.is_set():
                intersect = self.pool_1 & self.pool_2
                if intersect:
                    self.pool_1 -= intersect
                    self.pool_2 -= intersect
                break
            else:
                pass
