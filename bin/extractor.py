"""A single process module to call sdcflat and export flattened SDC commands to shared memory."""

__author__ = 'Lawrence Li'
__version__ = '2.0'
__date__ = 'Fri Feb 27 2015'


import subprocess, os, threading

sdcflat = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'sdcflat')


class Extractor(threading.Thread):

    def __init__(self, sdcfile, pool, cmd, product, errlog, lock):
        threading.Thread.__init__(self)
        self.sdcfile = sdcfile
        self.pool = pool
        self.cmd = cmd
        self.product = product
        self.errlog = errlog
        self.lock = lock


    def run(self):
        p = subprocess.Popen(args = [sdcflat, self.sdcfile, self.cmd, self.product],
                stdout = subprocess.PIPE, stderr = self.errlog)
        for ln in p.stdout:
            self.lock.acquire()
            self.pool.add(ln[:-1])
            self.lock.release()
        p.wait()


