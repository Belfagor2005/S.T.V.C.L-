import os, re, six
from twisted.web.client import downloadPage
print("stvcl.py")
def upd_done():
	print( "In upd_done")
	xfile ='http://patbuweb.com/stvcl/stvcl.tar'
	print('xfile: ', xfile)
	if six.PY3:
		xfile = b"http://patbuweb.com/stvcl/stvcl.tar"
	print("Update.py not in PY3")
	fdest = "/tmp/stvcl.tar"
	print("upd_done xfile =", xfile)
	downloadPage(xfile, fdest).addCallback(upd_last)

def upd_last(fplug):
	cmd = "tar -xvf /tmp/stvcl.tar -C /"
	print( "cmd A =", cmd)
	os.system(cmd)
	pass

