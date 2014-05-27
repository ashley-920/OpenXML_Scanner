import sys
import bitstring   # Used to parse data. Download from: http://code.google.com/p/python-bitstring/
import pefile      # Used to parse PE header. Download from: http://code.google.com/p/pefile/
from datetime import datetime
from Output_Item import Output_Item
import os

def log(string):
# This just tees output to a file and stdout
    # print string
    open('pe_carve.log', 'a').write(string + "\n")

def getSize_FromPE(PE_data):
# Performs basic lookup to find the end of an EXE, based upon the
# size of PE sections. Same algorithm is used to find EXE overlay
# FYI: This will miss any overlay data, such as RAR SFX archives, etc
    try:
        pe = pefile.PE(data=PE_data)
        return pe.sections[-1].PointerToRawData + pe.sections[-1].SizeOfRawData
    except:
        return 0

def process(fname,sample):
    # Start main
    pe_list=None
    
    time = datetime.now().strftime("[%d %b %y @ %H:%M:%S]")    
    log('Scan started on %s at %s' % (fname, time))
    list = []
    fstream = bitstring.ConstBitStream(filename = fname)
    results = fstream.findall(b'0x546869732070726F6772616D')  # "This program"
    log( "Gathering search hits...")
    for i in results:
        # The result offsets are stored as binary values, so you have to divide by 8
        # -78 is the negative offset to the beginning of "MZ" from "This program"
        hit = int(i)/8-78
        list.append(hit)


    log( "Parsing EXEs...")
    ifile = open(fname, 'rb')
    for hit in list:
        ifile.seek(hit)
        PE_header = ifile.read(1024)
        pesize = getSize_FromPE(PE_header)        
       
        if (10000 < pesize < 10000000) and PE_header[0:2] == "MZ":
            if pe_list == None:
                pe_list=[]
            log( "Found at: 0x%X (%d bytes)" % (hit, pesize))
            ifile.seek(hit)
            PE_data = ifile.read(pesize) 
            extract_pe_filename= "%s_%s_%X.livebin" % (sample.file_name,fname.split("/")[-1], hit) 
            pe_dir=os.path.join(sample.sample_dir,"PE_files")
            if not os.path.exists(pe_dir):
                os.makedirs(pe_dir)
            outfile = os.path.join(pe_dir,extract_pe_filename)
            open(outfile, 'wb').write(PE_data)
            pe_list.append(outfile)
        else:            
            log ("Ignored PE header at 0x%X" % hit)
        
    time = datetime.now().strftime("[%d %b %y @ %H:%M:%S]")   
    log( 'Scan ended on %s at %s' % (fname, time))
    
    return pe_list
