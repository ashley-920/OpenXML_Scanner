from Dissector import Dissector
from Sample import Sample
from Parser import Parser
from Extractor import Extractor
from Operator import Operator
from Config import Config
from Report_Generator import Report_Generator
import os,sys, zipfile
import olez





def process_sample(file_path):
    print file_path
    config=Config()
    load_sucess=config.load_config()
    if load_sucess:
        dis=Dissector()
        parser=Parser()
        extrator=Extractor()
        operator=Operator(config)
        r_generator=Report_Generator()
        sample=Sample(file_path)        
        rlt=dis.extract_file(sample,config.get_output_dir())   
        bin_time_list=list()     
        if rlt:                     
            parser.parse(sample)
            extrator.extract(sample)
            # config.print_info()      
            # operator.operate(sample,config)
            # r_generator.write_report(sample)   
            # try:         
            #     for bin in sample.bin_file_list:
            #         bin_path=os.path.join(sample.extract_file_dir,bin[0])                
            #         time=olez.OLE_Parser(bin_path)
            #         bin_time_list.append(time)
            #     bin_time_list=deduplicate(list(),bin_time_list)
            #     print bin_time_list
            # except Exception, e:
            #     print "Error when getting timestamp"
                
    return bin_time_list

    

        
        # sample.print_info()
    # all_types = Config.get_all_object_types()
    # # iterate through all object types
    # for object_type in all_types:
    #     # get necessary scanner for this type
    #     applied_scanners = Config.get_object_applied_scanner(object_type)
    #     for scanner in applied_scanners:
    #         do_scan(scanner, object_type)
    # sample.print_info()

def deduplicate(uni_list,_list):    
    for item in _list:
        if item not in uni_list:
            uni_list.append(item)
    return uni_list




def run(file_path):
    if os.path.isdir(file_path):
        dir_files_list=os.listdir(file_path)
        total_time_list=list()
        print len(dir_files_list)
        for files in dir_files_list:    
            bin_time_list=process_sample(os.path.join(file_path, files))
            total_time_list=deduplicate(total_time_list,bin_time_list)            
        print "Total time template:"
        print total_time_list
        
        # f=open("C:\Users\Ash\Desktop\python\openXML_scanner\cve_2013_3906_binary_timestamp.txt",'wb')
        # for time in total_time_list:
        #     f.write(time)
        #     f.write("\n")
        # f.close()


    else:
        process_sample(file_path)



if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv)>1:
        run(sys.argv[1])
    else:
        print "[file_path/dir_path]                          =>start process file"
