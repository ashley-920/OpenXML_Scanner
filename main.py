from Dissector import Dissector
from Sample import Sample
from Parser import Parser
from Extractor import Extractor
from Operator import Operator
from Config import Config
from Report_Generator import Report_Generator
import os,sys, zipfile





def process_sample(file_path):
    config=Config()
    load_sucess=config.load_config()
    if load_sucess:
        dis=Dissector()
        parser=Parser()
        extrator=Extractor()
        operator=Operator(config)
        r_generator=Report_Generator()
        sample=Sample(file_path)        
        dis.extract_file(sample,config.get_output_dir())             
        parser.parse(sample)
        extrator.extract(sample)
        # config.print_info()      
        operator.operate(sample,config)
        r_generator.write_report(sample)

        
        # sample.print_info()
    # all_types = Config.get_all_object_types()
    # # iterate through all object types
    # for object_type in all_types:
    #     # get necessary scanner for this type
    #     applied_scanners = Config.get_object_applied_scanner(object_type)
    #     for scanner in applied_scanners:
    #         do_scan(scanner, object_type)
    # sample.print_info()




def run(file_path):    
    if os.path.isdir(file_path):
        dir_files_list=os.listdir(file_path)
        for files in dir_files_list:    
            process_sample(os.path.join(file_path, files))
    else:
        process_sample(file_path)



if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv)>1:
        run(sys.argv[1])
    else:
        print "[file_path/dir_path]                          =>start process file"
