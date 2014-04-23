class XML_parser:

    dictionary=None



    def parseFile(self,file_path,file_name):
        try:
            remove_pattern=r"<!\[(\w+)\]>"
            remove_pattern2=r"<!\[(\w+\s\w+\s\w+\s\w+)\]>"
            file_path=file_path
            dfile=zipfile.ZipFile(file_path,'r')
            data= dfile.read(file_name)
            data=re.sub(remove_pattern,"", data.decode("utf-8"))
            data=re.sub(remove_pattern2,"", data)
                #print("data:",data)   
            self.dictionary=xmltodict.parse(data)  
                #dfile.close()
            return self.dictionary
        except:
            print("Read file Error")
            print(traceback.format_exc())
        else:
            pass
        finally:
            pass


    def get_dic(self):
        return self.dictionary

        



