from bs4 import BeautifulSoup
import os,re


class Config:

    config_file="config.xml"
    output_dir=None
    scanner_list=None
    objects_list=None

    # load the output path of dissected files (working directory)

    def load_config(self):
        config_path=os.path.join(os.path.dirname(__file__), self.config_file)       
        f=open(config_path,"r")
        config_data=f.read()
        f.close()
        soup = BeautifulSoup(config_data)
           
        #get output_dir    
        self.output_dir=str(unicode(soup.find("output_dir").string))        
        self.output_dir=re.sub("\t", "", self.output_dir)
        self.output_dir=re.sub("\n", "", self.output_dir)

        #get all scanner module
        self.scanner_list=list()
        scan_file_list=list()
        scanner_tag=soup.scanners
        for tag in scanner_tag.find_all("file"):
            file_list=list()
            scan_file_list.append(tag.parent.name)
            if tag["status"] == "on":
                file_list.append(tag.text)
            scan_file_list.append(file_list)
            self.scanner_list.append(scan_file_list)
   
        #get object list
        self.objects_list=list()
        objects_tag=soup.objects
        for tag in objects_tag.find_all("scan"):
            obj_mod=list()
            obj_mod.append(tag.parent.name)
            mod_list=tag.find_all("module")
            mod_list_string=list()
            if mod_list != None:
                for mod in mod_list:                
                    mod_list_string.append(mod.string)
            obj_mod.append(mod_list_string)
            self.objects_list.append(obj_mod)


        if self.output_dir != None and self.scanner_list !=None and self.objects_list != None:
            return True
        else:
            return False


    # get all object types that will be extracted from an xml file
    def get_objects_list(self):
        return self.objects_list
    # get the scanner's path
    def get_scanner_list(self, scanner_name):
        return self.scanner_list

    def get_output_dir(self):
        return self.output_dir



config=Config()
config.load_config()