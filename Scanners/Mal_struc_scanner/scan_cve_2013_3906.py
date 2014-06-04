from Utils import Utils
from Output_Item import Output_Item

def scan(file_path):
    ot=Output_Item()    
    iom=0
    report=""
    utils=Utils()
    timestamp_3906="2013-03-21 16:49:05.943"
    time=""
    try:
        time=utils.get_ole_timestamp(file_path)
    except Exception, e:
        print "Error when getting OLE timestamp:"+str(e)     
    if time == timestamp_3906:
        iom=200
        report="\nTimestamp of this binary match CVE 2013-3906 template\n"
    ot.set_item(iom,report)
    return ot


    