from bs4 import BeautifulSoup
import os,re


class Config:

    config_file="config.xml"
    output_dir=None
    scanner_dict=None
    objects_dict=None

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

        self.scanner_dict=dict()
        
        scanner_tag=soup.find_all("scanner")

        for tag in scanner_tag:
            file_list=list()
            file_list_item=tag.find_all("file")
            for file in file_list_item:
                if file["status"] == "on":
                    file_list.append(file.text)
            add_dict={tag["name"]:file_list}
            self.scanner_dict.update(add_dict)
            
       
        #get object list
        self.objects_dict=dict()
        objects_tag=soup.objects
        for tag in objects_tag.find_all("scan"):
            
            # obj_mod.append(tag.parent.name)
            mod_list=tag.find_all("module")
            mod_list_string=list()
            if mod_list != None:
                for mod in mod_list:                
                    mod_list_string.append(mod.string)
            # obj_mod.append(mod_list_string)
            add_dict={tag.parent.name:mod_list_string}
            self.objects_dict.update(add_dict)


        if self.output_dir != None and self.scanner_dict !=None and self.objects_dict != None:
            return True
        else:
            return False


    # get all object types that will be extracted from an xml file
    def get_objects_dict(self):
        return self.objects_dict
    # get the scanner's path
    def get_scanner_dict(self):
        return self.scanner_dict

    def get_output_dir(self):
        return self.output_dir

    def print_info(self):
        print "output_dir: ",self.output_dir
        print "scanner_dict:"
        for scanner in self.scanner_dict.keys():
            print "Scanner Module:",scanner
            for py in self.scanner_dict[scanner]:
                print py

        print "objects_dict:"        
        for obj in self.objects_dict.keys():
            print "Object:",obj
            for scanner in self.objects_dict[obj]:
                print scanner

        # print "objects_list",self.objects_list



# config=Config()
# config.load_config()