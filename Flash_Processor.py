from Flash_Object import Flash_Object
from Sample import Sample
import binascii, struct
import sys,re,os,subprocess as sub

class Flash_Processor:

	swftool_dir= "\\Modules\\swftools\\swfdump.exe"

	def process(self,sample):		
		sample.swf_dir=os.path.join(sample.sample_dir,"SWF_files")
		if not os.path.exists(sample.swf_dir):
			os.makedirs(sample.swf_dir)
		# print sample.swf_dir
		for bin in sample.bin_file_list:					
			bin_path=os.path.join(sample.extract_file_dir,bin[0])
			swf_list=self.extract_swf(bin_path)			
			for swf in swf_list:
				if not sample.file_contain_flash: 
					sample.file_contain_flash=True
				flash_obj=Flash_Object()
				flash_obj.file_size=len(swf[0])
				flash_obj.swf_type=swf[0][0:3]
				bin_name=os.path.basename(bin_path)				
				flash_obj.file_name = "[%s]_%s_%s_%08X" % (sample.file_name,bin_name, flash_obj.swf_type, swf[1])
				flash_obj.file_path=os.path.join(sample.swf_dir,flash_obj.file_name)
				self.write_to_swf(swf[0],flash_obj.file_path)
				flash_obj.as_file_name=flash_obj.file_name+".txt"
				flash_obj.as_file_path=os.path.join(sample.swf_dir,flash_obj.as_file_name)
				self.extract_actionscript(flash_obj.file_path,flash_obj.as_file_path)				
				sample.flash_obj_list.append(flash_obj)

			
			
	def getOffsetInFile(self,pattern, fn):
		data = str.upper(binascii.hexlify(fn))
		offs = []
		if len(data) > 0:
			p = re.compile(pattern)
			for m in p.finditer(data):
				offs.append(m.start()/2)
			return offs

	def extract_swf(self,bin_path):
		#read bin file
		f = open(bin_path, 'rb')
		bin = f.read()
		f.close()
		#get offset list
		cws_offset = self.getOffsetInFile(str.upper(binascii.hexlify('CWS')), bin)
		fws_offset = self.getOffsetInFile(str.upper(binascii.hexlify('FWS')), bin)

		# if cws_offset != 0 or fws_offset != 0:
		# 	offset=(cws_offset,fws_offset)[cws_offset>0]

		#extract swf by offset and len
		#parse "CWS" and "FWS",  but actually office will convert CWS to FWS when comppress
		
		swf_list=list()
		i = 0
		if cws_offset:
			for offs in cws_offset:
				# print "CWS"
				if bin[offs:offs+3] == 'CWS':
					ver = struct.unpack("B", bin[offs+3:offs+4])[0]
					if ver >=0 and ver <= 30:
						swf_len = struct.unpack('i', bin[offs+4:offs+8])[0]
						swf_list.append([bin[offs:offs+swf_len],offs])
		if fws_offset:
			for offs in fws_offset:
				# print "FWS"
				if bin[offs:offs+3] == 'FWS':
					ver = struct.unpack("B", bin[offs+3:offs+4])[0]
					if ver >=0 and ver <= 30:					
						swf_len = struct.unpack('i', bin[offs+4:offs+8])[0]
						swf_list.append([bin[offs:offs+swf_len],offs])				

		return swf_list

	def write_to_swf(self,swf,file_path):
		file_path=file_path+".swf"
		f = open(file_path, 'wb')
		f.write(swf)
		f.close()


	def extract_actionscript(self,file_path,des_text_path):		
		prog_swftools = os.path.dirname(__file__)+self.swftool_dir		
		test_command="\""+prog_swftools+"\" -a \""+file_path+"\" > \""+des_text_path+"\""
		# print test_command
		# print 'ActionScript file location:'
		# print  '*%s' % (des_text_path)
		sub.Popen(test_command,shell=True, stdout=sub.PIPE, stderr=sub.STDOUT)


if __name__ == '__main__':  # pragma: no cover
	if len(sys.argv)>1:
		processor=Flash_Processor()
		processor.process(sys.argv[1])
	else:
		print "Syntex : \n\t%s path" % sys.argv[0]