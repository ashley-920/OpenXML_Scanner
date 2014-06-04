from Sample import Sample
from bs4 import BeautifulSoup
import os,re
from Utils import Utils

class Parser:

    def parse(self,sample):
        self.get_file_type(sample)        
        self.get_ActiveX_Info(sample)
        self.get_ContentType_Info(sample)
        self.get_flash_info(sample)
        self.get_VBA_info(sample)
        self.get_bin_list(sample)


    def get_file_type(self,sample):     
        sample.file_type='unknown'
        for filename in sample.file_list:           
            if "word/document.xml" in filename:
                sample.file_type = 'DOCX'
                break
            elif "xl/workbook.xml" in filename:
                sample.file_type = 'XLSX'
                break
            elif "ppt/presentation.xml" in filename:
                sample.file_type = 'PPTX'
                break
        return sample.file_type;

    def get_ActiveX_Info(self,sample):       
        for item in sample.file_list:
            if "activeX" in item:
                if sample.file_contain_activeX!=True:
                    sample.file_contain_activeX=True
                break                    
                # print "File: ",item
        return sample.file_contain_activeX

    def get_bin_list(self,sample):
        utils=Utils()
        sample.bin_file_list=list()
        ole_timestamp=None
        for item in sample.file_list:
            if item.endswith(".bin"):
                bin_path=os.path.join(sample.extract_file_dir,item)
                md5=utils.md5_for_file(bin_path)
                try:
                    ole_timestamp=utils.get_ole_timestamp(bin_path)
                except Exception, e:
                    print "Error when getting OLE timestamp:"+str(e)                
                sample.bin_file_list.append([item,md5,ole_timestamp])                 
                # print "File: ",item
        return sample.bin_file_list

    def get_ContentType_Info(self,sample):            
        file_name=r"[Content_Types].xml"
        content_type_file_path=os.path.join(sample.extract_file_dir,file_name)
        # print content_type_file_path
        activeX_contentType="application/vnd.ms-office.activeX+xml"
        activeX_extension="bin"
        sample.partName_List=list()
        sample.extension_List=list()
        # remove_pattern=r"<!\[(\w+)\]>"
        # remove_pattern2=r"<!\[(\w+\s\w+\s\w+\s\w+)\]>"
        soup=self.get_soup(content_type_file_path)
        """
        check Override attri 
        #json=>content['Types']['Override'][0]['@PartName']    
        """
        # for item in soup.types.find_all(contenttype=activeX_contentType):
        #     sample.activeX_List.append(item.get('partname'))
        if len(soup.types.find_all(contenttype=activeX_contentType)) != 0:
            sample.file_contain_activeX=True
        """
        check Default attri
        #json=>content['Types']['Default'][0]['@Extension']    
        """
        #get extensions list
        for item in soup.types.find_all("default"):
            sample.extension_List.append(item.get('extension'))


    def get_flash_info(self,sample):
        #scan vml file and document.xml file
        flash_string="ShockwaveFlash"
        real_file_path=list()
        if sample.file_type == "PPTX" or sample.file_type == "XLSX":
            vml_path_pattern=r"/drawings/vmlDrawing[(0-9)+].vml"
            for name in sample.file_list:
                if re.search(vml_path_pattern,name)!=None:
                    real_file_path.append(os.path.join(sample.extract_file_dir,name))            
        elif sample.file_type == "DOCX":
            doc_path=r"word/document.xml"
            real_file_path.append(os.path.join(sample.extract_file_dir,doc_path))

        if len(real_file_path)>0:
            for path in real_file_path:
                # print path
                soup=self.get_soup(path)
                #find flash string in pptx or xlsx format
                if len(soup.find_all(id=re.compile(flash_string))) > 0:
                    sample.file_contain_flash=True
                #find flash string in docx format
                elif len(soup.find_all(attrs={"w:name":re.compile(flash_string)})) > 0:
                    sample.file_contain_flash=True                        
        else:
            print("No flash related xml file found")
        if sample.file_contain_flash == None:
            sample.file_contain_flash=False


    def get_VBA_info(self,sample):    
        vba_file='vbaProject.bin'      
        for filename in sample.file_list:
            if filename.endswith(vba_file):
                sample.file_contain_vba=True
                sample.vba_path=filename
                break
        if sample.file_contain_vba == None:
            sample.file_contain_vba=False
        return sample.file_contain_vba



    def get_soup(self,file_path):
        f=open(file_path,"r")
        data=f.read()
        f.close()
        soup = BeautifulSoup(data)
        return soup






