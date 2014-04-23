from Sample import Sample
from Flash_Processor import Flash_Processor
import OfficeMalHunter as OMH
import os

class Extractor:
    def extract(self,sample):
        if len(sample.bin_file_list)>0:
            flash_processor=Flash_Processor()
            flash_processor.process(sample)
        if sample.file_contain_vba:
            vba_path=os.path.join(sample.extract_file_dir,sample.vba_path)
            print vba_path
            OMH.print_stream_info(vba_path, None, sample.sample_dir)



