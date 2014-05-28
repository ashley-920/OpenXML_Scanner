from Sample import Sample
from Config import Config
import os
from bs4 import BeautifulSoup
import re
import zipfile
import sys
import hashlib
from Utils import Utils

class Dissector:




	# def load_output_dir(self):
	# 	config_path=os.path.join(os.path.dirname(__file__), self.config_file)		
	# 	f=open(config_path,"r")
	# 	config_data=f.read()
	# 	f.close()
	# 	soup = BeautifulSoup(config_data)		
	# 	self.output_dir=str(unicode(soup.find("output_dir").string))		
	# 	self.output_dir=re.sub("\t", "", self.output_dir)
	# 	self.output_dir=re.sub("\n", "", self.output_dir)
	# 	return self.output_dir

	def extract_file(self,sample,output_dir):		
	    # if output_dir==None:
	    # 	self.load_output_dir()
	    utils=Utils()
	    sample.file_md5=utils.md5_for_file(sample.file_path)
	    sample.file_name=os.path.basename(sample.file_path)	    
	    sample.sample_dir=os.path.join(output_dir,sample.file_name)
	    # print self.extract_file_dir
	    sample.extract_file_dir=os.path.join(sample.sample_dir,sample.file_name+u"_files")
	    if not os.path.exists(output_dir) or not os.path.isdir(output_dir):
	        os.makedirs(sample.extract_file_dir)	   
	    if zipfile.is_zipfile(sample.file_path):
	        dfile=zipfile.ZipFile(sample.file_path,'r')
	        sample.file_list=dfile.namelist()     
	        dfile.extractall(sample.extract_file_dir)
	        print "Extract "+sample.file_name+" to: "+sample.extract_file_dir+" Successfully"
	    return sample.file_list

	# def get_output_dir(self):
	# 	return output_dir
	


if __name__ == '__main__':  # pragma: no cover
	if len(sys.argv)>2:
		if sys.argv[1] == "-e":
			dis=Dissector()
			dis.extract_file(sys.argv[2])
		else:
			print "-e [file_path]                          => extract files"
	else:
		print "-e [file_path]                          => extract files"
