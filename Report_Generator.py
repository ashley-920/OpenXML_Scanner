import os


class Report_Generator:
    def write_report(self,sample):
        summary="\n################### Report Summary ###################\n"
        summary+="Sample File Path:"+sample.file_path+"\n"
        summary+="Sample File Name:"+sample.file_name+"\n"
        summary+="Sample File MD5: "+sample.file_md5+"\n"
        summary+="Sample Directory:"+sample.sample_dir+"\n"
        summary+="Sample Extract File Directory:"+sample.extract_file_dir+"\n"
        summary+="Sample File Type:"+sample.file_type+"\n"
        summary+="Sample File List:\n"

        c=0
        for file in sample.file_list:
            summary+="  ["+str(c)+"]"+file+"\n"
            c+=1
        if not sample.extension_List == None:
            summary+="Sample Extension List:\n"         
            for ext in sample.extension_List:
                summary+="  *"+ext+"\n"     
        if not sample.bin_file_list == None:
            summary+="Sample Binary List:\n"            
            for bin in sample.bin_file_list:
                summary+="  *"+bin[0]+"   , MD5="+bin[1]+"   , OLE timestamp="+str(bin[2])+"\n"

        
        if not sample.file_contain_flash == None:
            summary+="SWF File Directory:"+str(sample.swf_dir)+"\n"
            if not sample.flash_obj_list == None:
                summary+="Flash Object Number:"+str(len(sample.flash_obj_list))+"\n"
                c=0
                for flash in sample.flash_obj_list:
                    summary+="  Flash Object ["+str(c)+"]\n"
                    summary+="      File Name: "+flash.file_name+"\n"
                    summary+="      File Path: "+flash.file_path+"\n"
                    summary+="      File Size: "+str(flash.file_size)+"\n"
                    summary+="      Flash Header Type: "+flash.swf_type+"\n"
                    summary+="      ActionScript File Name: "+flash.as_file_name+"\n"
                    summary+="      ActionScript File Path: "+flash.as_file_path+"\n"
                    c+=1        
        if not sample.vba_dir == None:
            summary+="VBA File Path: "+sample.vba_path+"\n"
            summary+="VBA File Directory: "+sample.vba_dir+"\n"

        if sample.file_contain_pe:              
            if not sample.pe_file_list == None:
                summary+="PE File Number: "+str(len(sample.pe_file_list))+"\n"
                summary+="Extracted PE File List: \n"
                c=0
                for pe in sample.pe_file_list:
                    summary+="  ["+str(c)+"] "+pe+"\n"
                    c+=1



        summary+="\nIOM of this sample:"+str(sample.IOM)+"\n"
        summary+="\nHighlight:\n"
        if sample.exploit_20133906:
            summary+="\n* Sample Contain CVE 2013-3906 exploit\n\n"
        summary+="#######################################################\n"
        summary+="Report Detail:\n"

        sample.report=summary+sample.report
        report_file_name=sample.file_name+" Scanning Report.txt"
        output_path=os.path.join(sample.sample_dir,report_file_name)
        f=open(output_path,'w')
        f.write(sample.report)
        f.close()