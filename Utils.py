import hashlib

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