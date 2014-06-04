#!/usr/local/bin/python
# -*- coding: latin-1 -*-

import sys, os, struct, binascii, mmap, re

MAGIC = '\320\317\021\340\241\261\032\341'

used_streams_fat = []
used_streams_minifat = []

#[PL]: added constants for Sector IDs (from AAF specifications)
MAXREGSECT = 0xFFFFFFFAL; # maximum SECT
DIFSECT    = 0xFFFFFFFCL; # (-4) denotes a DIFAT sector in a FAT
FATSECT    = 0xFFFFFFFDL; # (-3) denotes a FAT sector in a FAT
ENDOFCHAIN = 0xFFFFFFFEL; # (-2) end of a virtual stream chain
FREESECT   = 0xFFFFFFFFL; # (-1) unallocated sector

#[PL]: added constants for Directory Entry IDs (from AAF specifications)
MAXREGSID  = 0xFFFFFFFAL; # maximum directory entry ID
NOSTREAM   = 0xFFFFFFFFL; # (-1) unallocated directory entry

#[PL] object types in storage (from AAF specifications)
STGTY_EMPTY     = 0 # empty directory entry (according to OpenOffice.org doc)
STGTY_STORAGE   = 1 # element is a storage object
STGTY_STREAM    = 2 # element is a stream object
STGTY_LOCKBYTES = 3 # element is an ILockBytes object
STGTY_PROPERTY  = 4 # element is an IPropertyStorage object
STGTY_ROOT      = 5 # element is a root storage

from ctypes import windll, Structure, c_ushort, byref, c_ulong, c_long

class SYSTEMTIME(Structure):
    _fields_ =  (
                ('wYear', c_ushort), 
                ('wMonth', c_ushort), 
                ('wDayOfWeek', c_ushort), 
                ('wDay', c_ushort), 
                ('wHour', c_ushort), 
                ('wMinute', c_ushort), 
                ('wSecond', c_ushort), 
                ('wMilliseconds', c_ushort), 
                )

class LONG_INTEGER(Structure):
    _fields_ =  (
            ('low', c_ulong), 
            ('high', c_long),
            )
            
def Print_TimeDateStamp(ft):
	FileTimeToSystemTime=windll.kernel32.FileTimeToSystemTime
	st = SYSTEMTIME(0,0,0,0,0,0,0,0)
	ft = LONG_INTEGER(ft.high, ft.low)
	r = FileTimeToSystemTime(byref(ft),byref(st))
	return '%4d-%02d-%02d %02d:%02d:%02d.%03d' % (st.wYear,st.wMonth,st.wDay,st.wHour,st.wMinute,st.wSecond,st.wMilliseconds)
	
def debug(msg):
	{}
	#print msg

#[PL] Experimental setting: if True, OLE filenames will be kept in Unicode
# if False (default PIL behaviour), all filenames are converted to Latin-1.
KEEP_UNICODE_NAMES = False

def _unicode(s, errors='replace'):
	"""
	Map unicode string to Latin 1. (Python with Unicode support)
	
	s: UTF-16LE unicode string to convert to Latin-1
	errors: 'replace', 'ignore' or 'strict'. See Python doc for unicode()
	"""
	#TODO: test if it OleFileIO works with Unicode strings, instead of
	#      converting to Latin-1.
	try:
		# First the string is converted to plain Unicode:
		# (assuming it is encoded as UTF-16 little-endian)
		u = s.decode('UTF-16LE', errors)
		if KEEP_UNICODE_NAMES:
			return u
		else:
			# Second the unicode string is converted to Latin-1
			return u.encode('latin_1', errors)
	except:
		# there was an error during Unicode to Latin-1 conversion:
		raise IOError, 'incorrect Unicode name'

def i16(c, o = 0):
	"""
	Converts a 2-bytes (16 bits) string to an integer.
	
	c: string containing bytes to convert
	o: offset of bytes to convert in string
	"""
	return ord(c[o])+(ord(c[o+1])<<8)


def i32(c, o = 0):
	"""
	Converts a 4-bytes (32 bits) string to an integer.
	
	c: string containing bytes to convert
	o: offset of bytes to convert in string
	"""
	return int(ord(c[o])+(ord(c[o+1])<<8)+(ord(c[o+2])<<16)+(ord(c[o+3])<<24))
	# [PL]: added int() because "<<" gives long int since Python 2.4

def _clsid(clsid):
	"""
	Converts a CLSID to a human-readable string.
	clsid: string of length 16.
	"""
	assert len(clsid) == 16
	if clsid == "\0" * len(clsid):
		return ""
	return (("%08X-%04X-%04X-%02X%02X-" + "%02X" * 6) % ((i32(clsid, 0), i16(clsid, 4), i16(clsid, 6)) + tuple(map(ord, clsid[8:16]))))
	
def _check_duplicate_stream(first_sect, minifat=False):
	"""
	Checks if a stream has not been already referenced elsewhere.
	This method should only be called once for each known stream, and only
	if stream size is not null.
	first_sect: index of first sector of the stream in FAT
	minifat: if True, stream is located in the MiniFAT, else in the FAT
	"""
	global used_streams_fat
	global used_streams_minifat
	
	if minifat:
		debug('_check_duplicate_stream: sect=%d in MiniFAT' % first_sect)
		used_streams = used_streams_minifat
	else:
		debug('_check_duplicate_stream: sect=%d in FAT' % first_sect)
		# some values can be safely ignored (not a real stream):
		if first_sect in (DIFSECT,FATSECT,ENDOFCHAIN,FREESECT):
			return
		used_streams = used_streams_fat
	#TODO: would it be more efficient using a dict or hash values, instead
	#      of a list of long ?
	if first_sect in used_streams:
		debug('Stream referenced twice')
	else:
		used_streams.append(first_sect)

def OLE_Parser(path):

	with open(path, 'r+b') as f:
		map = mmap.mmap(f.fileno(), 0)
		filesize = map.size()
		offs = 0
		
		#print path
		
		header = map[offs:offs+512]

		# [PL] header structure according to AAF specifications:
		#Header
		#struct StructuredStorageHeader { // [offset from start (bytes), length (bytes)]
		#BYTE 	_abSig[8]; 								// [00H,08] {0xd0, 0xcf, 0x11, 0xe0, 0xa1, 0xb1,
		#                									// 0x1a, 0xe1} for current version
		#CLSID 	_clsid;   								// [08H,16] reserved must be zero (WriteClassStg/
		#                									// GetClassFile uses root directory class id)
		#USHORT _uMinorVersion; // [18H,02] minor version of the format: 33 is
		#                       // written by reference implementation
		#USHORT _uDllVersion;   // [1AH,02] major version of the dll/format: 3 for
		#                       // 512-byte sectors, 4 for 4 KB sectors
		#USHORT _uByteOrder;    // [1CH,02] 0xFFFE: indicates Intel byte-ordering
		#USHORT _uSectorShift;  // [1EH,02] size of sectors in power-of-two;
		#                       // typically 9 indicating 512-byte sectors
		#USHORT _uMiniSectorShift; // [20H,02] size of mini-sectors in power-of-two;
		#                          // typically 6 indicating 64-byte mini-sectors
		#USHORT _usReserved; // [22H,02] reserved, must be zero
		#ULONG _ulReserved1; // [24H,04] reserved, must be zero
		#FSINDEX _csectDir; // [28H,04] must be zero for 512-byte sectors,
		#                   // number of SECTs in directory chain for 4 KB
		#                   // sectors
		#FSINDEX _csectFat; // [2CH,04] number of SECTs in the FAT chain
		#SECT _sectDirStart; // [30H,04] first SECT in the directory chain
		#DFSIGNATURE _signature; // [34H,04] signature used for transactions; must
		#                        // be zero. The reference implementation
		#                        // does not support transactions
		#ULONG _ulMiniSectorCutoff; // [38H,04] maximum size for a mini stream;
		#                           // typically 4096 bytes
		#SECT _sectMiniFatStart; // [3CH,04] first SECT in the MiniFAT chain
		#FSINDEX _csectMiniFat; // [40H,04] number of SECTs in the MiniFAT chain
		#SECT _sectDifStart; // [44H,04] first SECT in the DIFAT chain
		#FSINDEX _csectDif; // [48H,04] number of SECTs in the DIFAT chain
		#SECT _sectFat[109]; // [4CH,436] the SECTs of first 109 FAT sectors
		#};

		if len(header) != 512 or header[:8] != MAGIC:
			print "not an OLE2 structured storage file"
			# return

		fmt_header = '<8s16sHHHHHHLLLLLLLLLL'
		header_size = struct.calcsize(fmt_header)
		debug( "fmt_header size = %d, +FAT = %d" % (header_size, header_size + 109*4) )
		header1 = header[:header_size]
		(
			Sig,
			clsid,
			MinorVersion,
			DllVersion,
			ByteOrder,
			SectorShift,
			MiniSectorShift,
			Reserved, Reserved1,
			csectDir,
			csectFat,
			sectDirStart,
			signature,
			MiniSectorCutoff,
			MiniFatStart,
			csectMiniFat,
			sectDifStart,
			csectDif
		) = struct.unpack(fmt_header, header1)
		debug(struct.unpack(fmt_header, header1))

		if Sig != '\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
			# OLE signature should always be present
			debug("incorrect OLE signature")
#			if clsid != '\x00'*16:
#				# according to AAF specs, CLSID should always be zero
#				debug("incorrect CLSID in OLE header")

		debug( "MinorVersion = %d" % MinorVersion )
		debug( "DllVersion   = %d" % DllVersion )
		if DllVersion not in [3, 4]:
			# version 3: usual format, 512 bytes per sector
			# version 4: large format, 4K per sector
			debug("incorrect DllVersion in OLE header")
			
		debug( "ByteOrder    = %X" % ByteOrder )
		if ByteOrder != 0xFFFE and ByteOrder != 0x00FE and ByteOrder != 0xFFFF and ByteOrder != 0xFF00:
			# For now only common little-endian documents are handled correctly
			debug("incorrect ByteOrder in OLE header")
			# TODO: add big-endian support for documents created on Mac ?
			
		SectorSize = 2**SectorShift
		debug( "SectorSize   = %d" % SectorSize )
		if SectorSize not in [512, 4096]:
			debug("incorrect SectorSize in OLE header")
			
		if (DllVersion==3 and SectorSize!=512) or (DllVersion==4 and SectorSize!=4096):
			debug("SectorSize does not match DllVersion in OLE header")
			
		MiniSectorSize = 2**MiniSectorShift
		debug( "MiniSectorSize   = %d" % MiniSectorSize )
		if MiniSectorSize not in [64]:
			debug("incorrect MiniSectorSize in OLE header")

		if Reserved != 0 or Reserved1 != 0:
			debug("incorrect OLE header (non-null reserved bytes)")

		debug( "csectDir     = %d" % csectDir )
		if SectorSize==512 and csectDir!=0:
			debug("incorrect csectDir in OLE header")

		debug( "csectFat     = %d" % csectFat )
		debug( "sectDirStart = %X" % sectDirStart )
		debug( "signature    = %d" % signature )
		
		# Signature should be zero, BUT some implementations do not follow this
		# rule => only a potential defect:
		if signature != 0:
			debug("incorrect OLE header (signature>0)")
			
		debug( "MiniSectorCutoff = %d" % MiniSectorCutoff )
		debug( "MiniFatStart     = %X" % MiniFatStart )
		debug( "csectMiniFat     = %d" % csectMiniFat )
		debug( "sectDifStart     = %X" % sectDifStart )
		debug( "csectDif         = %d" % csectDif )

		# calculate the number of sectors in the file
		# (-1 because header doesn't count)
		nb_sect = ( (filesize + SectorSize-1) / SectorSize) - 1
		debug( "Number of sectors in the file: %d" % nb_sect )

		# file clsid (probably never used, so we don't store it)
		clsid = _clsid(header[8:24])
		sectorsize = SectorSize #1 << i16(header, 30)
		minisectorsize = MiniSectorSize  #1 << i16(header, 32)
		minisectorcutoff = MiniSectorCutoff # i32(header, 56)

		# check known streams for duplicate references (these are always in FAT,
		# never in MiniFAT):
		_check_duplicate_stream(sectDirStart)
		# check MiniFAT only if it is not empty:
		if csectMiniFat:
		    _check_duplicate_stream(MiniFatStart)
		# check DIFAT only if it is not empty:
		if csectDif:
		    _check_duplicate_stream(sectDifStart)

#        # Load file allocation tables
#        loadfat(header)
#        # Load direcory.  This sets both the direntries list (ordered by sid)
#        # and the root (ordered by hierarchy) members.
#        loaddirectory(sectDirStart)#i32(header, 48))
#        ministream = None
#        minifatsect = MiniFatStart #i32(header, 60)


		# struct to parse directory entries:
		# <: little-endian byte order
		# 64s: string containing entry name in unicode (max 31 chars) + null char
		# H: uint16, number of bytes used in name buffer, including null = (len+1)*2
		# B: uint8, dir entry type (between 0 and 5)
		# B: uint8, color: 0=black, 1=red
		# I: uint32, index of left child node in the red-black tree, NOSTREAM if none
		# I: uint32, index of right child node in the red-black tree, NOSTREAM if none
		# I: uint32, index of child root node if it is a storage, else NOSTREAM
		# 16s: CLSID, unique identifier (only used if it is a storage)
		# I: uint32, user flags
		# 8s: uint64, creation timestamp or zero
		# 8s: uint64, modification timestamp or zero
		# I: uint32, SID of first sector if stream or ministream, SID of 1st sector
		#    of stream containing ministreams if root entry, 0 otherwise
		# I: uint32, total stream size in bytes if stream (low 32 bits), 0 otherwise
		# I: uint32, total stream size in bytes if stream (high 32 bits), 0 otherwise

		if sectDirStart == 0:
			DirStartAddr = 1 << SectorShift
		else:
			DirStartAddr = (sectDirStart << SectorShift) + (header_size + 109*4)
		
		debug(hex(DirStartAddr))
		
		if DirStartAddr > filesize:
			print( "OLE corrupt DirStart over filesize" + path )
			return
		
		sid = 0
		while True:
			STRUCT_DIRENTRY = '<64sHBBIII16sI8s8sIII'
			# size of a directory entry: 128 bytes
			DIRENTRY_SIZE = 128
			assert struct.calcsize(STRUCT_DIRENTRY) == DIRENTRY_SIZE

			entry = map[DirStartAddr+(sid*DIRENTRY_SIZE):DirStartAddr+(sid*DIRENTRY_SIZE)+DIRENTRY_SIZE]

#			if entry > filesize:
#				return
			
			try:
				(
					name,
					namelength,
					entry_type,
					color,
					sid_left,
					sid_right,
					sid_child,
					e_clsid,
					dwUserFlags,
					createTime,
					modifyTime,
					isectStart,
					sizeLow,
					sizeHigh
				) = struct.unpack(STRUCT_DIRENTRY, entry)
			except:
				return

			if entry_type not in [STGTY_ROOT, STGTY_STORAGE, STGTY_STREAM, STGTY_EMPTY]:
				debug('unhandled OLE storage type')
			# only first directory entry can (and should) be root:
			if entry_type == STGTY_ROOT and sid != 0:
				debug('duplicate OLE root entry')
			if sid == 0 and entry_type != STGTY_ROOT:
				debug('incorrect OLE root entry')

			# name should be at most 31 unicode characters + null character,
			# so 64 bytes in total (31*2 + 2):
			if namelength > 64:
				debug ('incorrect DirEntry name length')
				# if exception not raised, namelength is set to the maximum value:
				namelength = 64
			# only characters without ending null char are kept:
			name = name[:(namelength-2)]
			# name is converted from unicode to Latin-1:
			name = _unicode(name)
			
			#print name
			if name in ('WordDocument', 'worddocument', 'Worddocument'):
				print 'DOC %s' % path
				break
				
			if name in ('Workbook', 'workbook', 'WorkbooK'):
				print 'XLS %s' % path
				break
				
			if name in ('PowerPoint Document', 'Pictures'):
				print 'PPT %s' % path
				break

			if name in ('Catalog'):
				print 'Thumbs.db %s' % path
				break
				
			if name.find('substg') != -1:
				print 'MSG %s' % path
				break

			debug('DirEntry SID=%d: %s' % (sid, repr(name)))
			debug(' - type: %d' % entry_type)
			debug(' - sect: %d' % isectStart)
			debug(' - SID left: %d, right: %d, child: %d' % (sid_left, sid_right, sid_child))
			
			if sid == 0:
#				high = int(struct.unpack("L", createTime[0:4])[0])
#				low = int(struct.unpack("L", createTime[4:8])[0])
#				ft = LONG_INTEGER(low & 0xFFFFFFFFL, high >>32)
#				print "createTime : %s" % Print_TimeDateStamp(ft)
				high = int(struct.unpack("L", modifyTime[0:4])[0])
				low = int(struct.unpack("L", modifyTime[4:8])[0])
				ft = LONG_INTEGER(low & 0xFFFFFFFFL, high >>32)
				# print binascii.hexlify(modifyTime[0:8])
				# print "%s,%s" % (Print_TimeDateStamp(ft), path)



			# sizeHigh is only used for 4K sectors, it should be zero for 512 bytes
			# sectors, BUT apparently some implementations set it as 0xFFFFFFFFL, 1
			# or some other value so it cannot be raised as a defect in general:
			if sectorsize == 512:
				if sizeHigh != 0 and sizeHigh != 0xFFFFFFFFL:
					debug('sectorsize=%d, sizeLow=%d, sizeHigh=%d (%X)' % (sectorsize, sizeLow, sizeHigh, sizeHigh))
					debug('incorrect OLE stream size')
				size = sizeLow
			else:
				size = sizeLow + (long(sizeHigh)<<32)
				
			debug(' - size: %d (sizeLow=%d, sizeHigh=%d)' % (size, sizeLow, sizeHigh))
			
			if sid > 32: # i dont know that how to quit the loop, also i brute 32 times.
				break
				
			e_clsid = _clsid(e_clsid)
			# a storage should have a null size, BUT some implementations such as
			# Word 8 for Mac seem to allow non-null values => Potential defect:
			if entry_type == STGTY_STORAGE and size != 0:
				debug('OLE storage with size>0')
			# check if stream is not already referenced elsewhere:
			if entry_type in (STGTY_ROOT, STGTY_STREAM) and size>0:
				if size < minisectorcutoff and entry_type==STGTY_STREAM: # only streams can be in MiniFAT
					# ministream object
					minifat = True
				else:
					minifat = False
				_check_duplicate_stream(isectStart, minifat)
			sid+=1

	map.close()
	f.close()
	return Print_TimeDateStamp(ft)
	
if __name__ == '__main__':
	if len(sys.argv) >= 2:
		OLE_Parser(sys.argv[1])
	else:
		print "Syntex : \n\t%s filename" % sys.argv[0]
