#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
PY3 = sys.version_info.major >= 3
print("Update.py")


def upd_done():
    from os import popen, remove
    cmd01 = "wget http://patbuweb.com/stvcl/stvcl.tar -O /tmp/stvcl.tar ; tar -xvf /tmp/stvcl.tar -C /"
    cmd02 = "wget --no-check-certificate -U 'Enigma2 - stvcl Plugin' -c 'http://patbuweb.com/stvcl/stvcl.tar' -O '/tmp/stvcl.tar'; tar -xvf /tmp/stvcl.tar -C /"
    cmd22 = 'find /usr/bin -name "wget"'
    res = popen(cmd22).read()
    if 'wget' not in res.lower():
        if os.path.exists('/etc/opkg'):
            cmd23 = 'opkg update && opkg install wget'
        else:
            cmd23 = 'apt-get update && apt-get install wget'
    try:
        popen(cmd02)
    except:
        popen(cmd01)
    remove('/tmp/stvcl.tar')
    return



# import sys
# PY3 = sys.version_info.major >= 3
# print("Update.py")
# fdest = "/tmp/stvcl.tar"


# def upd_done():
    # from twisted.web.client import downloadPage
    # print("In upd_done")
    # xfile = 'http://patbuweb.com/stvcl/stvcl.tar'
    # if PY3:
        # xfile = b"http://patbuweb.com/stvcl/stvcl.tar"
        # print("Update.py in PY3")
    # import requests
    # response = requests.head(xfile)
    # fdest = "/tmp/stvcl.tar"
    # if response.status_code == 200:
        # # print(response.headers['content-length'])
        # print("Code 200 upd_done xfile =", xfile)
        # downloadPage(xfile, fdest).addCallback(upd_last)
    # elif response.status_code == 404:
        # print("Error 404")
    # else:
        # return


# def upd_last(fplug):
    # import time
    # import os
    # time.sleep(5)
    # fdest = "/tmp/stvcl.tar"
    # if os.path.isfile(fdest) and os.stat(fdest).st_size > 10000:
        # cmd = "tar -xvf /tmp/stvcl.tar -C /"
        # print("cmd A =", cmd)
        # os.system(cmd)
        # os.remove('/tmp/stvcl.tar')
    # return
