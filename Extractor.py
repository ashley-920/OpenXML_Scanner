from Sample import Sample
from Flash_Processor import Flash_Processor
from Utils import Utils
import OfficeMalHunter as OMH
import os
import Modules.PE_Carver.pe_carve as pe_carve


class Extractor:

    utils=Utils()
    
    def extract(self,sample):
        # print sample.bin_file_list
        if len(sample.bin_file_list)>0:
            flash_processor=Flash_Processor()
            flash_processor.process(sample)
        if sample.file_contain_vba:
            vba_path=os.path.join(sample.extract_file_dir,sample.vba_path)
            try:                
                # OMH.print_stream_info(vba_path, None, sample.sample_dir)
                self.decompile_vba(vba_path)
                # copy file to sample dir then delete
                copy_dir=os.path.dirname(__file__)+"\\VBAPROJECT.BIN-Macros"
                print "copy dir= "+copy_dir
                if sample.vba_dir == None:
                    sample.vba_dir=os.path.join(sample.sample_dir,"Macros")
                if not os.path.exists(sample.vba_dir):
                    os.makedirs(sample.vba_dir)

                if os.path.exists(copy_dir):
                    print "dir exist"
                    for file in os.listdir(copy_dir):
                        file_name=file
                        src_path=os.path.join(copy_dir,file)
                        dst_path=sample.vba_dir+"\\"+file
                        self.utils.copy_and_remove_file(src_path,dst_path)


                
                print "Extract VBA success"
                
            except Exception, e:
                print "Error when extract VBA script"
                sample.report=sample.report+"Error when extract VBA script"
        #try to scan and extract PE in bin file
        for bin in sample.bin_file_list:
            obs_bin_path=os.path.join(sample.extract_file_dir,bin[0])
            try:
                rlt=pe_carve.process(obs_bin_path,sample)           
                if rlt:                             
                    sample.file_contain_pe=True
                    sample.pe_file_list=rlt[:]   
            except Exception, e:   
                print "Error when extracting pe"
                sample.report=sample.report+"Error when extracting pe"          
        


            # print sample.pe_file_list

    def decompile_vba(self,bin_file_path):
        utils=Utils()
        prog_path=os.path.dirname(__file__)+"\\Modules\\OfficeMalScanner\\OfficeMalScanner.exe"
        command="\""+prog_path+"\" \""+bin_file_path+"\" info"
        try:
            self.utils.run_command(prog_path,command)
        except Exception,e:
            print "Error When decompile VBA: "+str(e)







