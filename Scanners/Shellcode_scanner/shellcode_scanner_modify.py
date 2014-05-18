import os, sys, re
from struct import unpack
from ctypes import *

import binascii

# from ctypes import byref
# from ctypes import c_byte
# from ctypes import c_char_p

# RATING
# Malicious index rating:
#   Executables: 4
#   Code       : 3
#   STRINGS    : 2
#   OLE/NOPs   : 1
RATING_EXEC   = 4
RATING_CODE   = 3
RATING_STRS   = 2
RATING_OLENOP = 1

A8            = c_byte * 8
g_aOfficeSig  = A8( 0xD0, 0xCF, 0x11, 0xE0, 0xA1, 0xB1, 0x1A, 0xE1 )

A6            = c_byte * 6
g_FldzSig     = A6( 0xD9, 0xEE, 0xD9, 0x74, 0x24, 0xF4 )
g_CallPopSig1 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x58 )
g_CallPopSig2 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x59 )
g_CallPopSig3 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x5A )
g_CallPopSig4 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x5B )
g_CallPopSig5 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x5E )
g_CallPopSig6 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x5F )
g_CallPopSig7 = A6( 0xE8, 0x00, 0x00, 0x00, 0x00, 0x5D )

A5            = c_byte * 5
g_FS30Sig1    = A5( 0x64, 0xA1, 0x30, 0x00, 0x00 ) # MOV EAX,DWORD PTR FS:[30]
g_FS30Sig2    = A5( 0x64, 0x8B, 0x1D, 0x30, 0x00 ) # MOV EBX,DWORD PTR FS:[30]
g_FS30Sig3    = A5( 0x64, 0x8B, 0x0D, 0x30, 0x00 ) # MOV ECX,DWORD PTR FS:[30]
g_FS30Sig4    = A5( 0x64, 0x8B, 0x15, 0x30, 0x00 ) # MOV EDX,DWORD PTR FS:[30]
g_FS30Sig5    = A5( 0x64, 0x8B, 0x35, 0x30, 0x00 ) # MOV ESI,DWORD PTR FS:[30]
g_FS30Sig6    = A5( 0x64, 0x8B, 0x3D, 0x30, 0x00 ) # MOV EDI,DWORD PTR FS:[30]

A3            = c_byte * 3
g_NopSig      = A3( 0x90, 0x90, 0x90 )

APIZ          = [
    'UrlDownloadToFile',
    'GetTempPath',
    'GetWindowsDirectory',
    'GetSystemDirectory',
    'WinExec',
    'IsBadReadPtr',
    'IsBadWritePtr',
    'CreateFile',
    'CloseHandle',
    'ReadFile',
    'WriteFile',
    'SetFilePointer',
    'VirtualAlloc',
    'GetProcAddr',
    'LoadLibrary']

g_power       = 0 # indicate the malicious power
g_f_name      = '' 



def scan_shellcode(file_path):
    global g_f_name
    g_f_name = os.path.basename(file_path)
    try:
        f = open(file_path,'rb')
        mappedfile = f.read()
        f.close()
        
        # shell_list=shellcode_scanner(mappedfile) 
        # if len(shell_list)==0:
        #     print "No shellcode found"
        # else:
        #     print shell_list

    except IOError as err:
        print("I/O Error: {0}".format(err))
    except:
        print("Generic Error Happened\n")
    omh_shellcode_scan(mappedfile)



def omh_shellcode_scan(g_f_cnt):
    global g_power
    global g_f_name
    mode_flg  = 0 # <scan | info> mode
    debug_flg = 0
    brute_flg = 0

    libc = cdll.msvcrt
    k32  = windll.kernel32
    h = k32.GetStdHandle( 0xFFFFFFF5 ) # STD_OUTPUT_HANDLE
    g_f_size = len(g_f_cnt)

    output=""

    print "[*] Scanning now...\n\n",
    output=output+"\n[*] Scanning now...\n\n"
    for i in xrange(g_f_size):
        if ( libc.memcmp( byref(g_FS30Sig1), g_f_cnt[i:], 5 ) == 0 or
            libc.memcmp( byref(g_FS30Sig2), g_f_cnt[i:], 5 ) == 0 or
            libc.memcmp( byref(g_FS30Sig3), g_f_cnt[i:], 5 ) == 0 or
            libc.memcmp( byref(g_FS30Sig4), g_f_cnt[i:], 5 ) == 0 or
            libc.memcmp( byref(g_FS30Sig5), g_f_cnt[i:], 5 ) == 0 or
            libc.memcmp( byref(g_FS30Sig6), g_f_cnt[i:], 5 ) == 0 ):
            print "FS:[30h] (Method 1) signature found at offset: 0x%x\n" % i,
            output=output+"FS:[30h] (Method 1) signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x6A and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x30 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x64 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0x8B ):
            print "FS:[30] (Method 2) signature found at offset: 0x%x\n" % i,
            output=output+"FS:[30] (Method 2) signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x33 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xB3 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0x64 and
            unpack( 'B', g_f_cnt[i+5] )[0] == 0x8B ):
            print "FS:[30] (Method 3) signature found at offset: 0x%x\n" % i,
            output=output+"FS:[30] (Method 3) signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x74 and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xC1 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0x0D and
            unpack( 'B', g_f_cnt[i+5] )[0] == 0x03 ):
            print "API-Hashing signature found at offset: 0x%x\n" % i,
            output=output+"API-Hashing signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x55 and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x8B and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xEC and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x83 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0xC4 ):
            print "Function prolog signature found at offset: 0x%x\n" % i,
            output=output+"Function prolog signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x55 and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x8B and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xEC and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x81 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0xEC ):
            print "Function prolog signature found at offset: 0x%x\n" % i,
            output=output+"Function prolog signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xFF and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x75 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xFF and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0x55 ):
            print "PUSH DWORD[]/CALL[] signature found at offset: 0x%x\n" % i,
            output=output+"PUSH DWORD[]/CALL[] signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x34 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xAA ):
            print "LODSB/STOSB XOR decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB XOR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x04 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xAA ):
            print "LODSB/STOSB ADD decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB XOR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x2C and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xAA ):
            print "LODSB/STOSB SUB decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB SUB decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xD0 and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xC0 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xAA ):
            print "LODSB/STOSB ROL decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB ROL decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xD0 and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xC8 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0xAA ):
            print "LODSB/STOSB ROR decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB ROR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xC0 and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xC0 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0xAA ):
            print "LODSB/STOSB ROL decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB ROL decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAC and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xC0 and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0xC8 and
            unpack( 'B', g_f_cnt[i+4] )[0] == 0xAA ):
            print "LODSB/STOSB ROR decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSB/STOSB ROR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x35 and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+7] )[0] == 0xAB ):
            print "LODSW/STOSW XOR decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSW/STOSW XOR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x05 and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+7] )[0] == 0xAB ):
            print "LODSW/STOSW ADD decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSW/STOSW ADD decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+2] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+3] )[0] == 0x2D and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0x66 and
            unpack( 'B', g_f_cnt[i+7] )[0] == 0xAB ):
            print "LODSW/STOSW SUB decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSW/STOSW SUB decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x35 and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0xAB ):
            print "LODSD/STOSD XOR decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSD/STOSD XOR decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x05 and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0xAB ):
            print "LODSD/STOSD ADD decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSD/STOSD ADD decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i]   )[0] == 0xAD and
            unpack( 'B', g_f_cnt[i+1] )[0] == 0x2D and
            unpack( 'B', g_f_cnt[i+6] )[0] == 0xAB ):
            print "LODSD/STOSD SUB decryption signature found at offset: 0x%x\n" % i,
            output=output+"LODSD/STOSD SUB decryption signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if libc.memcmp( byref(g_FldzSig), g_f_cnt[i:], 6 ) == 0:
            print "FLDZ/FSTENV [esp-12] signature found at offset: 0x%x\n" % i,
            output=output+"FLDZ/FSTENV [esp-12] signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        if ( libc.memcmp( byref(g_CallPopSig1), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig2), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig3), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig4), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig5), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig6), g_f_cnt[i:], 6 ) == 0 or
                libc.memcmp( byref(g_CallPopSig7), g_f_cnt[i:], 6 ) == 0 ):
            print "CALL next/POP signature found at offset: 0x%x\n" % i,
            output=output+"CALL next/POP signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            g_power += RATING_CODE

        
        
        if ( unpack( 'B', g_f_cnt[i] )[0] == 0xEB ):
            # print binascii.hexlify(g_f_cnt[i+1])
            # print i, g_f_size
            if(i<=g_f_size-2):
                if(i+unpack('B',g_f_cnt[i+1])[0]+2<g_f_size) :
                    # unpack( 'B', g_f_cnt[i+unpack('B',g_f_cnt[i+1])[0]+2] )[0] == 0xE8 ):
                    jmp_off  = i + unpack('B',g_f_cnt[i+1])[0] + 2
            #                call_va  = unpack( '<L', g_f_cnt[jmp_off+1:jmp_off+5] )[0]  # python is much simple
                    call_va  = unpack( 'B', g_f_cnt[jmp_off + 1] )[0]
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 2] )[0] << 8
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 3] )[0] << 16
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 4] )[0] << 24
                    if ( jmp_off + call_va + 5 < g_f_size):
                        if( unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x58 or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x59 or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5A or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5B or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5E or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5F ):
                            print "JMP [0xEB]/CALL/POP signature found at offset: 0x%x\n" % i,
                            output=output+"JMP [0xEB]/CALL/POP signature found at offset: "+hex(i)+"\n"
                            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
                            g_power += RATING_CODE

        if ( unpack( 'B', g_f_cnt[i] )[0] == 0xE9 ):
            # print binascii.hexlify(g_f_cnt[i+1])
            # print i, g_f_size
            if(i<=g_f_size-2):
                if(i+unpack('B',g_f_cnt[i+1])[0]+5<g_f_size) :
                    # unpack( 'B', g_f_cnt[i+unpack('B',g_f_cnt[i+1])[0]+2] )[0] == 0xE8 ):
                    jmp_off  = i + unpack('B',g_f_cnt[i+1])[0] + 5
            #                call_va  = unpack( '<L', g_f_cnt[jmp_off+1:jmp_off+5] )[0]  # python is much simple
                    call_va  = unpack( 'B', g_f_cnt[jmp_off + 1] )[0]
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 2] )[0] << 8
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 3] )[0] << 16
                    call_va += unpack( 'B', g_f_cnt[jmp_off + 4] )[0] << 24
                    if ( jmp_off + call_va + 5 < g_f_size):
                        if( unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x58 or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x59 or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5A or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5B or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5E or
                           unpack( 'B', g_f_cnt[jmp_off+call_va+5] )[0] == 0x5F ):
                            print "JMP [0xE9]/CALL/POP signature found at offset: 0x%x\n" % i,
                            output=output+"JMP [0xE9]/CALL/POP signature found at offset: "+hex(i)+"\n"
                            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
                            g_power += RATING_CODE

        if ( libc.memcmp( c_char_p("MZ"), g_f_cnt[i:], 2 ) == 0 ):
            pe_off  = unpack( 'B', g_f_cnt[i+0x3C] )[0]
            pe_off += unpack( 'B', g_f_cnt[i+0x3D] )[0] << 8
            pe_off += unpack( 'B', g_f_cnt[i+0x3E] )[0] << 16
            pe_off += unpack( 'B', g_f_cnt[i+0x3F] )[0] << 24
            if ( libc.memcmp( c_char_p("PE"), g_f_cnt[i+pe_off:], 2 ) == 0):
                print "unencrypted MZ/PE signature found at offset: 0x%x\n" % i,
                output=output+"unencrypted MZ/PE signature found at offset: "+hex(i)+"\n"
                if debug_flg == 1: dump_data( "PE-File", g_f_cnt[i:], 0x100 )
                g_power += RATING_EXEC

    i = 0
    while ( i < g_f_size ):        
        if ( libc.memcmp( byref(g_NopSig), g_f_cnt[i:], 3 ) == 0 ):
            print "NOP slides signature found at offset: 0x%x\n" % i,
            output=output+"NOP slides signature found at offset: "+hex(i)+"\n"
            if debug_flg == 1: print_opcodz( g_f_cnt[i:] )
            while unpack('B', g_f_cnt[i])[0] == 0x90: i += 1
            g_power += RATING_OLENOP
        i += 1

    # for api in APIZ:
    #     for i in xrange(g_f_size):
    #         if libc.memcmp( c_char_p(api), g_f_cnt[i:], len(api) ) == 0:
    #             print "API-Name %s string found at offset: 0x%x\n" % (api, i),
    #             if debug_flg == 1: dump_data( "PE-File", g_f_cnt[i:], 0x100 )
    #             g_power += RATING_STRS
    # for i in xrange(8, g_f_size):
    #     if libc.memcmp( byref(g_aOfficeSig), g_f_cnt[i:], 8 ) == 0:
    #         print "Embedded OLE signature found at offset: 0x%x\n" % i,
    #         if debug_flg == 1: dump_data( "PE-File", g_f_cnt[i:], 0x100 )
    #         g_power += RATING_OLENOP

        
    print "\n\nAnalysis finished!\n\n",
    output=output+"\n\nAnalysis finished!\n\n"

    if g_power:
        k32.SetConsoleTextAttribute( h, 0x0E ) # FOREGROUND_GREEN or FOREGROUND_RED or FOREGROUND_INTENSITY
        libc.printf( "---------------------------------------------" )
        output=output+"---------------------------------------------"
        i = 0
        while i < len(g_f_name):
            libc.printf("-")
            i += 1
        libc.printf( "\n%s seems to be malicious! Malicious Index = %02d\n", g_f_name, g_power )
        libc.printf( "---------------------------------------------" )
        output=output+"\n"+g_f_name+" seems to be malicious! Malicious Index = "+str(g_power)+"\n"
        output=output+"---------------------------------------------"
        i = 0
        while i < len(g_f_name):
            libc.printf("-")
            output=output+"-"
            i += 1
        k32.SetConsoleTextAttribute( h, 0x0F ) # FOREGROUND_BLUE or FOREGROUND_GREEN or FOREGROUND_RED or FOREGROUND_INTENSITY
    else:
        k32.SetConsoleTextAttribute( h, 0x07 ) # FOREGROUND_BLUE or FOREGROUND_GREEN or FOREGROUND_RED
        print "---------------------------------------------------------------------\n",
        print "             No malicious traces found in this file!\n",
        print "Assure that this file is being scanned with the \"info\" parameter too.\n",
        print "---------------------------------------------------------------------\n",
        output=output+"---------------------------------------------------------------------\n"
        output=output+"             No malicious traces found in this file!\n"
        output=output+"Assure that this file is being scanned with the \"info\" parameter too.\n"
        output=output+"---------------------------------------------------------------------\n"
        k32.SetConsoleTextAttribute( h, 0x0F ) # FOREGROUND_BLUE or FOREGROUND_GREEN or FOREGROUND_RED or FOREGROUND_INTENSITY

    print output

def shellcode_scanner(mappedOle):

    shellcode_presence = list()

    match = re.search(b'\x64\x8b\x64',mappedOle)
    if match is not None:
        shellcode_presence.append("FS:[00] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x64\xa1\x00',mappedOle)
    if match is not None:
        shellcode_presence.append("FS:[00] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x64\xa1\x30\x00\x00',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))
        
    match = re.search(b'\x64\x8b\x1d\x30\x00',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))
        
    match = re.search(b'\x64\x8b\x0d\x30\x00',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x64\x8b\x15\x30\x00',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x64\x8b\x35\x30',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x64\x8b\x3d\x30',mappedOle) 
    if match is not None:
        shellcode_presence.append("FS:[30h] Shellcode at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x55\x8b\xec\x83\xc4',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Prolog at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x55\x8b\xec\x81\xec',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Prolog at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x55\x8b\xec\xe8',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Prolog at offset:{0}".format(hex(match.start())))

    match = re.search(b'\x55\x8b\xec\xe9',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Prolog at offset:{0}".format(hex(match.start())))
        
    match = re.search(b'\x90\x90\x90\x90',mappedOle)
    if match is not None:
        shellcode_presence.append("NOP Slide:{0}".format(hex(match.start())))
        
    match = re.search(b'\xd9\xee\xd9\x74\x24\xf4',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xe8\x00\x00\x00\x00\x58',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xe8\x00\x00\x00\x00\x59',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xe8\x00\x00\x00\x00\x5a',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
    
    match = re.search(b'\xe8\x00\x00\x00\x00\x5e',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xe8\x00\x00\x00\x00\x5f',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xe8\x00\x00\x00\x00\x5d',mappedOle)
    if match is not None:
        shellcode_presence.append("Call Pop Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xd9\xee\xd9\x74\x24\xf4',mappedOle)
    if match is not None:
        shellcode_presence.append("Fldz Signature:{0}".format(hex(match.start())))
        
    match = re.search(b'\xac\xd0\xc0\xaa',mappedOle)
    if match is not None:
        shellcode_presence.append("LODSB/STOSB ROL decryption:{0}".format(hex(match.start())))
        
    match = re.search(b'\xac\xd0\xc8\xaa',mappedOle)
    if match is not None:
        shellcode_presence.append("LODSB/STOSB ROR decryption:{0}".format(hex(match.start())))
        
    match = re.search(b'\x66\xad\x66\x35',mappedOle)
    if match is not None:
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+6])[0] == 0x66 and
             unpack('B',mappedOle[start_shcod+7])[0] == 0xAB ):
                 shellcode_presence.append("LODSW/STOSW XOR decryption signature:{0}".format(hex(start_shcod)))
        
    match = re.search(b'\x66\xad\x66\x05',mappedOle)
    if match is not None:
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+6])[0] == 0x66 and
             unpack('B',mappedOle[start_shcod+7])[0] == 0xAB ):
                 shellcode_presence.append("LODSW/STOSW ADD decryption signature:{0}".format(hex(start_shcod)))
        
    match = re.search(b'\x66\xad\x66\x2d',mappedOle)
    if match is not None:
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+6])[0] == 0x66 and
             unpack('B',mappedOle[start_shcod+7])[0] == 0xAB ):
                shellcode_presence.append("LODSW/STOSW SUB decryption signature:{0}".format(hex(start_shcod)))
    
    match = re.search(b'\xac\xc0\xc0',mappedOle)
    if match is not None:
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+4])[0] == 0xAA ):
            shellcode_presence.append("LODSB/STOSB ROL decryption signature:{0}".format(hex(start_shcod)))            
            
    match = re.search(b'\xac\xc0\xc8',mappedOle)
    if match is not None:
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+4])[0] == 0xAA ):
            shellcode_presence.append("LODSB/STOSB ROR decryption signature:{0}".format(hex(start_shcod)))
            
    
    for match in re.finditer(b'\xac\x34',mappedOle):
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+3])[0] == 0xAA ):
            shellcode_presence.append("LODSB/STOSB XOR decryption signature:{0}".format(hex(start_shcod)))
            print("Shellcode XOR Key is: " + hex(unpack('B',mappedOle[start_shcod+2])[0]))
                        
    for match in re.finditer(b'\xac\x04',mappedOle):        
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+3])[0] == 0xAA ):
            shellcode_presence.append("LODSB/STOSB ADD decryption signature:{0}".format(hex(start_shcod)))
            print("Shellcode ADD Key is: " + hex(unpack('B',mappedOle[start_shcod+2])[0]))
            
    for match in re.finditer(b'\xac\x2c',mappedOle):
        start_shcod = match.start()
        if ( unpack('B',mappedOle[start_shcod+3])[0] == 0xAA ):
            shellcode_presence.append("LODSB/STOSB ADD decryption signature:{0}".format(hex(start_shcod)))
            print("Shellcode SUB Key is: " + hex(unpack('B',mappedOle[start_shcod+2])[0]))

    

    return shellcode_presence


if __name__ == '__main__':
    if len(sys.argv) >= 2:
        scan_shellcode(sys.argv[1])
    else:
        print "Syntex : \n\t%s path" % sys.argv[0]