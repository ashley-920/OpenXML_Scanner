import hashlib
import olez
import shutil,os
import subprocess as sub
import thread

class Utils:
    def md5_for_file(self,file, block_size=2**20):
        f=open(file,"rb")
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest() 


    def get_ole_timestamp(self,file_path):
        return olez.OLE_Parser(file_path)

    def copy_and_remove_file(self,src,dst):
        print "copy "+src+" to "+dst
        #copy
        shutil.copyfile(src,dst)
        #remove
        os.remove(src)

    def run_command(self,prog_path,command):
        # lock=thread.allocate_lock()
        # thread.start_new_thread(self.do_command,(prog_path,command,lock))
        print "running command:"
        print command
        sub.Popen(command,shell=True, stdout=sub.PIPE, stderr=sub.STDOUT)
        

    def do_command(self,prog_path,command,lock):
        lock.acquire()
        copy_dir=os.path.dirname(__file__)+"\\VBAPROJECT.BIN-Macros"
        print "running command:"
        print command
        sub.Popen(command,shell=True, stdout=sub.PIPE, stderr=sub.STDOUT)
        lock.release()



