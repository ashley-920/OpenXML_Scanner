from Output_Item import Output_Item
import re,os
import pdb

def scan(file_path):
    # print "I am scanning VBA on file:", file_path
    vba_malicious_script=None

    ot=Output_Item()    
    url_count=0
    iom=0
    report=""
    path=os.path.dirname(__file__)+"\malicious_vba_list.txt"
    with open(path, 'r') as f:
        vba_malicious_script=f.readlines()
    f.close()
    # print vba_malicious_script

    f = open(file_path, 'r')
    data=f.read()
    # print data
    f.close()
    
    for pattern in vba_malicious_script:
        pattern=pattern.strip('\n')
        regex=re.compile(pattern,re.I)
        match=regex.findall(data)
        # pdb.set_trace()
        # print "\nPattern: "+pattern+", Match: "+str(len(match))+"\n"
        report=report+"\nPattern: "+pattern+", Match: "+str(len(match))+"\n"
        iom+=len(match)*10

    ot.set_item(iom,report)

    return ot

if __name__ == '__main__':
    scan_file_url(sys.argv[1])

    