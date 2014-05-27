from Sample import Sample
from Flash_Processor import Flash_Processor
import OfficeMalHunter as OMH
import os
import Modules.PE_Carver.pe_carve as pe_carve

class Extractor:
    def extract(self,sample):
        if len(sample.bin_file_list)>0:
            flash_processor=Flash_Processor()
            flash_processor.process(sample)
        if sample.file_contain_vba:
            vba_path=os.path.join(sample.extract_file_dir,sample.vba_path)
            # print vba_path
            OMH.print_stream_info(vba_path, None, sample.sample_dir)
            sample.vba_dir=os.path.join(sample.sample_dir,"Macros")
        #try to scan and extract PE in bin file
        for bin in sample.bin_file_list:
        	obs_bin_path=os.path.join(sample.extract_file_dir,bin)
        	rlt=pe_carve.process(obs_bin_path,sample)        	
        	if rlt:        		        		
        		sample.file_contain_pe=True
        		sample.pe_file_list=rlt[:]        		
        


        	# print sample.pe_file_list





