from Config import Config
from Flash_Object import Flash_Object
from Utils import Utils
import importlib,os
import Output_Item




class Operator:
    
    # call scanner's interface to scan all extracted objects of "obj_type"
    import_files=None
    objects_dict=None
    scanners_dict=None

    def __init__(self,config):
        self.objects_dict=config.get_objects_dict()
        self.scanners_dict=config.get_scanner_dict()


    def operate(self,sample, config):
        utils=Utils()
        import_file_dir="Scanners"
        
        if self.objects_dict != None and self.scanners_dict != None:

            # deal with activeX obj
            sample.report+="\n\n[Binary File Info]\n\n"         
            if sample.file_contain_activeX:
                
                # print "Contain activeX"
                scanners=self.objects_dict.get("activex")
                for scanner in scanners:
                    md5_list=list()
                    sample.report+="\n\n************************"+scanner+"*****************************\n\n"
                    # print scanner
                    files=self.scanners_dict.get(scanner)
                    for file in files:
                        file= os.path.splitext(file)[0]
                        import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
                        print "import "+import_path
                        module=self.import_files(import_path)
                        for bin in sample.bin_file_list:
                            if sample.exploit_20133906 and scanner == "Shellcode_scanner":
                                sample.report+="\n==========Skip Scanning since CVE 2013-3906 detected==========\n"
                                break
                            obs_bin_path=os.path.join(sample.extract_file_dir,bin[0])  
                            print "Path: "+obs_bin_path                          
                            if bin[1] not in md5_list:
                                print "not in md5 list"
                                sample.report+="\nFile: "+obs_bin_path+"\n"                            
                                sample.report+="\nMD5: "+bin[1]+"\n"
                                md5_list.append(bin[1])
                                rlt=self.scan_file(module, obs_bin_path)
                                if not rlt == None:
                                    if "CVE 2013-3906" in rlt.get_report():
                                        sample.exploit_20133906=True
                                    sample.IOM+=rlt.get_IOM()
                                    sample.report=sample.report+rlt.get_report()
                                    sample.report=sample.report+"\n--------------------------------------------------------------\n"


                            
                            
        
            #deal with flash object
            sample.report+="\n\n[Flash File Info]\n\n"
            if sample.file_contain_flash:
                # print "Contain Flash"
                scanners=self.objects_dict.get("action_script")
                print self.objects_dict
                for scanner in scanners:
                    sample.report+="\n\n************************"+scanner+"*****************************\n\n"
                    # print scanner
                    files=self.scanners_dict.get(scanner)
                    for file in files:
                        file= os.path.splitext(file)[0]
                        import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
                        module=self.import_files(import_path)
                        for flash_obj in sample.flash_obj_list:
                            print flash_obj.as_file_path                            
                            rlt=self.scan_file(module, flash_obj.as_file_path)
                            if not rlt == None:
                                sample.IOM+=rlt.get_IOM()
                                sample.report=sample.report+rlt.get_report()

            #deal with vba script
            sample.report+="\n\n[VBA File Info]\n\n"
            if sample.file_contain_vba:
                # print "Contain VBA"
                scanners=self.objects_dict.get("vba_script")
                # print self.objects_dict
                for scanner in scanners:
                    sample.report+="\n\n************************"+scanner+"*****************************\n\n"
                    # print scanner
                    files=self.scanners_dict.get(scanner)
                    for file in files:
                        file= os.path.splitext(file)[0]
                        import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
                        module=self.import_files(import_path)
                        for vba_file in os.listdir(sample.vba_dir):
                            vba_file_path=os.path.join(sample.vba_dir,vba_file)                         
                            rlt=self.scan_file(module, vba_file_path)
                            if not rlt == None:
                                sample.IOM+=rlt.get_IOM()
                                sample.report=sample.report+rlt.get_report()
                            

            #deal with xml file
            sample.report+="\n\n[XML File Info]\n\n"
            if sample.file_list != None:
                # print "Scan xml file"
                scanners=self.objects_dict.get("xml")
                for scanner in scanners:
                    sample.report+="\n\n************************"+scanner+"*****************************\n\n"
                    # print scanner
                    files=self.scanners_dict.get(scanner)
                    for file in files:
                        file= os.path.splitext(file)[0]
                        import_path= "%s.%s.%s" % (import_file_dir,scanner,file)
                        module=self.import_files(import_path)
                        for f in sample.file_list:
                            if f.endswith("xml"):
                                xml_file_path=os.path.join(sample.extract_file_dir,f)
                                rlt=self.scan_file(module, xml_file_path)
                                if not rlt == None:
                                    sample.IOM+=rlt.get_IOM()
                                    sample.report=sample.report+rlt.get_report()

            #deal with pe file
            sample.report+="\n\n[PE File Info]\n\n"
            if sample.file_contain_pe:
                print "file_contain_pe"
                print sample.pe_file_list
                sample.IOM+=len(sample.pe_file_list)*200

        print "IOM of This Sample:",sample.IOM
        print "Report of This Sample:",sample.report
        


    def import_files(self,file_name):
        module=importlib.import_module(file_name)
        return module

    def scan_file(self,module,file_path):
        return module.scan(file_path)



    

