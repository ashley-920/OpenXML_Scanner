from Config import Config
import importlib,os


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
			print "operating"
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
							self.scan_file(module, obs_bin_path)
						
			
		# scanner=self.import_files("Scanners.Shellcode_scanner.scan_shell")
		# scanner.scan()

		


	def import_files(self,file_name):
		module=importlib.import_module(file_name)
		return module

	def scan_file(self,module,file_path):
		module.scan(file_path)

		
