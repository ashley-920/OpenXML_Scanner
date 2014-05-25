from Config import Config
from Flash_Object import Flash_Object
import importlib,os
import Output_Item



class Operator:
	
	# call scanner's interface to scan all extracted objects of "obj_type"
	import_files=None
	objects_dict=None
	scanners_dict=None

	def __init__(self,config):
		self.objects_dict=config.get_objects_dict()
		self.scanners_dict=config.get_scanner_dict()


	def operate(self,sample, config):
		import_file_dir="Scanners"
		if self.objects_dict != None and self.scanners_dict != None:

			# deal with activeX obj			
			if sample.file_contain_activeX:
				print "Contain activeX"
				scanners=self.objects_dict.get("activex")
				for scanner in scanners:
					print scanner
					files=self.scanners_dict.get(scanner)
					for file in files:
						file= os.path.splitext(file)[0]
						import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
						module=self.import_files(import_path)
						for bin in sample.bin_file_list:
							obs_bin_path=os.path.join(sample.extract_file_dir,bin)
							rlt=self.scan_file(module, obs_bin_path)
							sample.IOM+=rlt.get_IOM()
							sample.report=sample.report+rlt.get_report()
		
			#deal with flash object
			if sample.file_contain_flash:
				print "Contain Flash"
				scanners=self.objects_dict.get("action_script")
				print self.objects_dict
				for scanner in scanners:
					print scanner
					files=self.scanners_dict.get(scanner)
					for file in files:
						file= os.path.splitext(file)[0]
						import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
						module=self.import_files(import_path)
						for flash_obj in sample.flash_obj_list:
							print flash_obj.as_file_path							
							rlt=self.scan_file(module, flash_obj.as_file_path)
							sample.IOM+=rlt.get_IOM()
							sample.report=sample.report+rlt.get_report()

			#deal with vba script
			if sample.file_contain_vba:
				print "Contain VBA"
				scanners=self.objects_dict.get("vba_script")
				# print self.objects_dict
				for scanner in scanners:
					print scanner
					files=self.scanners_dict.get(scanner)
					for file in files:
						file= os.path.splitext(file)[0]
						import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
						module=self.import_files(import_path)
						for vba_file in os.listdir(sample.vba_dir):
							vba_file_path=os.path.join(sample.vba_dir,vba_file)							
							rlt=self.scan_file(module, vba_file_path)
							sample.IOM+=rlt.get_IOM()
							sample.report=sample.report+rlt.get_report()
							

			#deal with xml file
			if sample.file_list != None:
				print "Scan xml file"
				scanners=self.objects_dict.get("xml")
				for scanner in scanners:
					print scanner
					files=self.scanners_dict.get(scanner)
					for file in files:
						file= os.path.splitext(file)[0]
						import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
						module=self.import_files(import_path)
						for f in sample.file_list:
							if f.endswith("xml"):
								xml_file_path=os.path.join(sample.extract_file_dir,f)
								rlt=self.scan_file(module, xml_file_path)
								sample.IOM+=rlt.get_IOM()
								sample.report=sample.report+rlt.get_report()

			#deal with pe file
			if sample.file_contain_pe:
				print "file_contain_pe"

			self.write_report(sample)
			print "IOM of This Sample:",sample.IOM
			print "Report of This Sample:",sample.report


	def import_files(self,file_name):
		module=importlib.import_module(file_name)
		return module

	def scan_file(self,module,file_path):
		return module.scan(file_path)

	def write_report(self,sample):
		summary="\n################### Report Summary ###################\n"
		summary+="Sample File Path:"+sample.file_path+"\n"
		summary+="Sample File Name:"+sample.file_name+"\n"
		summary+="Sample Directory:"+sample.sample_dir+"\n"
		summary+="Sample Extract File Directory:"+sample.extract_file_dir+"\n"
		summary+="Sample File Type:"+sample.file_type+"\n"
		summary+="Sample File List:\n"
		c=0
		for file in sample.file_list:
			summary+="	["+str(c)+"]"+file+"\n"
			c+=1
		if not sample.extension_List == None:
			summary+="Sample Extension List:\n"			
			for ext in sample.extension_List:
				summary+="	*"+ext+"\n"		
		if not sample.bin_file_list == None:
			summary+="Sample Binary List:\n"			
			for bin in sample.bin_file_list:
				summary+="	*"+bin+"\n"
		
		if not sample.file_contain_flash == None:
			summary+="SWF File Directory:"+sample.swf_dir+"\n"
			if not sample.flash_obj_list == None:
				summary+="Flash Object Number:"+str(len(sample.flash_obj_list))+"\n"
				c=0
				for flash in sample.flash_obj_list:
					summary+="Flash Object ["+str(c)+"]\n"
					summary+="	File Name: "+flash.file_name+"\n"
					summary+="	File Path: "+flash.file_path+"\n"
					summary+="	File Size: "+str(flash.file_size)+"\n"
					summary+="	Flash Header Type: "+flash.swf_type+"\n"
					summary+="	ActionScript File Name: "+flash.as_file_name+"\n"
					summary+="	ActionScript File Path: "+flash.as_file_path+"\n"
					c+=1		
		if not sample.vba_dir == None:
			summary+="VBA File Path:"+sample.vba_path+"\n"
			summary+="VBA File Directory:"+sample.VBA_dir+"\n"
		
		summary+="\nIOM of this sample:"+str(sample.IOM)+"\n\n"
		summary+="#######################################################\n"
		summary+="Report Detail:\n"

		sample.report=summary+sample.report
		report_file_name=sample.file_name+" Scanning Report.txt"
		output_path=os.path.join(sample.sample_dir,report_file_name)
		f=open(output_path,'w')
		f.write(sample.report)
		f.close()

