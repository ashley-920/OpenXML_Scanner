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
        
        scanner_tag=soup.find_all("scanner")
        # print scanner_tag.findChildren()

        for tag in scanner_tag:
            print tag["name"]
            scanner_list_item=list()
            scanner_list_item.append(tag["name"])
            # file_list=list()
            file_list=list()
            file_list_item=tag.find_all("file")
            for file in file_list_item:
                if file["status"] == "on":
                    file_list.append(file.text)
            scanner_list_item.append(file_list)
            self.scanner_list.append(scanner_list_item)

        
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

    def print_info(self):
        print "output_dir: ",self.output_dir
        print "scanner_list:"
        for scanner in self.scanner_list:
            print "Scanner Module:",scanner[0]
            for py in scanner[1]:
                print py

        print "objects_list",self.objects_list



# config=Config()
# config.load_config()