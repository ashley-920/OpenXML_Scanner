class Sample:
	file_path=None             #input file path
	file_name=None             #file base name
	extract_file_dir=None      #extract file dir path
	sample_dir=None            #sample's folder
	file_list=None             #extract files list
	file_type=None             #docx, xlsx, pptx 
	swf_dir=None               #swf files folder
	file_contain_activeX=None  #sample contain ActiveX or not
	file_contain_flash=None    #sample contain flash object or not
	file_contain_vba=None      #wether this file contain vba script
	file_contain_pe=None       #sample contain pe or not
	vba_path=None              #path of vbaProject.bin
	bin_file_list=None         #list of all bin file
	flash_obj_list=None        #list of all flash swf files
	extension_List=None        #list of all extension type in this file
	vba_dir=None               #VBA script directory
	IOM=0					   #indicator of malicious
	report=""                #scanning report

	def __init__(self,path):
		self.file_path=path
		self.bin_file_list=list()
		self.flash_obj_list=list()
		self.extension_List=list()

	def get_files_list(self):    
		return self.file_list

	def get_files_dir(self):
		return self.file_dir	

	def print_info(self):
		print "file_path:",self.file_path
		print "file_name: ",self.file_name
		print "sample_dir: ",self.sample_dir
		print "swf_dir",self.swf_dir
		print "extract_file_dir: ",self.extract_file_dir
		print "file_list: ",self.file_list
		print "file_type: ",self.file_type
		print "file_contain_activeX: ",self.file_contain_activeX
		print "file_contain_flash: ",self.file_contain_flash
		print "file_contain_vba: ",self.file_contain_vba
		# print "contentType_List: ",self.contentType_List
		print "extension_List: ",self.extension_List
		print "bin_file_list: ",self.bin_file_list
		print "flash_obj_list: ",self.flash_obj_list
		print "vba_dir: ",self.vba_dir