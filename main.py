from Dissector import Dissector
from Sample import Sample
from Parser import Parser
from Extractor import Extractor
import os,sys, zipfile

def run(file_path):
    dis=Dissector()
    parser=Parser()
    extrator=Extractor()
    if os.path.isdir(file_path):
        dir_files_list=os.listdir(file_path)
        for files in dir_files_list:    
            sample=Sample(os.path.join(file_path,files))
            dis.extract_file(sample)            
            parser.parse(sample)
            extrator.extract(sample)
            sample.print_info()
            

        
    else:
        sample=Sample(file_path)        
        dis.extract_file(sample)             
        parser.parse(sample)
        extrator.extract(sample)
        sample.print_info()



if __name__ == '__main__':  # pragma: no cover
    if len(sys.argv)>1:
        run(sys.argv[1])
    else:
        print "[file_path/dir_path]                          =>start process file"