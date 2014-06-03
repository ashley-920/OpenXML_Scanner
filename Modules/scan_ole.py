import os, sys
import string
import re

import yara
import mmap
from olez import OLE_Parser
import ctypes, ctypes.wintypes

def process_file(file_path):
	OLE_Parser(file_path)

def find_file(dir_name):
	FILE_ATTRIBUTE_DIRECTORY = 0x10
	INVALID_HANDLE_VALUE = -1
	
	BAN = (u'.', u'..')
	PATH = u''
	
	FindFirstFile = ctypes.windll.kernel32.FindFirstFileW
	FindNextFile  = ctypes.windll.kernel32.FindNextFileW
	FindClose     = ctypes.windll.kernel32.FindClose
	
	out  = ctypes.wintypes.WIN32_FIND_DATAW()
	fldr = FindFirstFile(os.path.join(dir_name, u'*'), ctypes.byref(out))

	while (fldr != INVALID_HANDLE_VALUE):
		if out.cFileName not in BAN:
			PATH = os.path.join(dir_name, out.cFileName)
			if (out.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY == FILE_ATTRIBUTE_DIRECTORY):
				find_file(PATH)
			else:
				process_file(PATH)

		if not FindNextFile(fldr, ctypes.byref(out)):
			break

	FindClose(fldr)	

if __name__ == '__main__':
	print "backdoor v0.1 scanner"
	
	if len(sys.argv) >= 2:
		find_file(sys.argv[1])
	else:
		print "Syntex : \n\t%s path" % sys.argv[0]

