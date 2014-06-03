import shutil,os

src="C:\\Users\\Ash\\Downloads\\OfficeMalScanner (4)\\VBAPROJECT.BIN-Macros\\ThisDocument"
dst="D:\\tmp2\\ThisDocument.txt"

shutil.copyfile(src,dst)

#remove
os.remove(src)