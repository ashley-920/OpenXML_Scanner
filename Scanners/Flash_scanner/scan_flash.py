from Output_Item import Output_Item

def scan(file_path):
	print "I am scanning AS on file:", file_path
	ot=Output_Item()	
	url_count=0
	iom=0
	report=""

	ot.set_item(iom,report)


	return ot

if __name__ == '__main__':
	scan_file_url(sys.argv[1])