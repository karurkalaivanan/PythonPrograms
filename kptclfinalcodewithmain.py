import datetime
from random import randint
from time import sleep
import socket
import sys
import time
import calendar
import binascii
import datetime
import codecs
import requests
from datetime import date
import datetime
from datetime import datetime
import serial
import time
import json
import redis
import pytz
import base64
import os
from pathlib import Path
ist = pytz.timezone('Asia/Kolkata')
import serial.tools.list_ports


#==============================ENCRYPTION FUNCTIONS==============================

key = "tl2CxESUsQsQNNspCY4GHw"


#================================================================================
# os.popen("sudo -S chmod 777 /dev/ttyUSB0", 'w').write('123456789')

# ---------------------------REDIS---------------------------

# redis_client1 = redis.Redis(host='localhost', port=6379, db=2)

# -------------------------- Variables -----------------------------------

finalstring = ""
metermake = "03"
special_counter = 0
hex_values = ""
METER_DEBUG = 1
response_buffer = []
frame_complete = False
Block_response = False
final_block = False
gwid = ""
PhaseType = 3
nodeid = ""
LoadStatus = 0
debug = 1

entry = "" 
fromentry = "" 
toentry = ""
meterslno = "Null"

LoadStatus = 0
lct = ""
rtc =""
metertype = ""
#//////////////////////////////// rtc variables ////////////////////////////////// 

g_year = ""
g_month = ""
g_day = ""
g_minutes = ""
g_seconds = ""
g_startingHour = ""

# //////////////////////////////// Profile variables /////////////////////////////////////

ipsvpacket = "0"
ipobpacket = "0"
ippacket = "0"
isobpacket ="0"
lsobpacket = "0"
lpobpacket = "0"
lpsvpacket = "0"
lpacket = "0"
bsvpacket = "0"
bsobpacket = "0"
bobpacket = "0"
bpacket = "0"
esvpacket = "0"
esobpacket = "0"
eobpacket = "0"

gw_current_firmware_version = 1.1

meters = [
    "LT",
    "MAXWELL",
    "LG",
    "SECURE",
    "HPL",
    "GENUS",
    "CAP",
    "EEPL",
    "KELLER"
]


# ////   passwords ///////

passwordsofmeter = ["lnt1",   #// lnt
                   "mx201199", #// maxwell
                   "11111111", #// LNG 
                   "ABCD0001",     #// secure
                   "1111111111111111",#// HPL
                   "1A2B3C4D", #// GENUS
                   "123456", #//CAP
                   "ABCDEFGH",
                   "KEL_SEC1"
                   ] #// EEPL

LLS_Keys = ""  

countofeventsoccured = 0

# /////////////////////////////////////////////redis variables///////////////////////////////////////

ipob = 0
isob = 0
ipsv = 0
lpob = 0
lsob = 0
lpsv = 0
bob = 0
bsv = 0
bsob = 0
eob = 0
esob = 0
esv = 0
rtc = 0
loadcapturetime = 0
configflag = 0

# ////////////////////////////////////////////////////////////////////////////////////////////////////

def crc(msg):
    poly = 0x8408
    crc = 0xffff
    for byte in msg:
        for _ in range(8):
            if (byte ^ crc) & 1:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            byte >>= 1
    return crc ^ 0xffff

# Global counters initialized
g_RRR = 0
g_SSS = 0

def get_sequence_number(nAct):
    global g_RRR, g_SSS
    # print(g_RRR,g_SSS)
    cFrameType = 0
    if nAct == 0:
        g_RRR += 1
        if g_RRR > 0x07:
            g_RRR = 0
    elif nAct == 1:
        g_SSS += 1
        if g_SSS > 0x07:
            g_SSS = 0
    elif nAct == 2:
        cFrameType = (g_RRR << 5) | 0x10
        cFrameType |= (g_SSS << 1)
    elif nAct == 3:
        cFrameType = (g_RRR << 5) | 0x10
        cFrameType |= 0x01
    return cFrameType


def bit_read(value, bit_position):
    return (value >> bit_position) & 1

def aarqframing():
    try:
        global g_RRR,g_SSS
        g_RRR = 0
        g_SSS = 0

        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(2)
        get_sequence_number(1);
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        hdlc = "E6E600"
        TAG_AARQ = "60"
        clinetapplicationcontext = "80020284"
        app_ctxt_name_1 = "A109060760857405080101"
        aARQ_aCSE_rEQs = "8A020780"
        auth_mech_name_1 = "8B0760857405080201"
        llsleng1 = format(2+len(LLS_Keys),'#04x')
        llsleng1 = llsleng1[2:]
        llsleng2 = format(len(LLS_Keys),'#04x')
        llsleng2 = llsleng2[2:]    
        password_tag = "AC"+str(llsleng1)+"80"+str(llsleng2)
        password = LLS_Keys.encode('utf-8').hex()
        auth_password_or_public_Tag_len = "BE10040E"
        xDlmsRequest1 = "01000000065F1F0400001E1DFFFF" 
        lasttag = "7E"

        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(clinetapplicationcontext)+len(app_ctxt_name_1)+len(aARQ_aCSE_rEQs)+len(auth_mech_name_1)+len(password_tag)+len(password)+len(auth_password_or_public_Tag_len)+len(xDlmsRequest1)+8+4)/2)
        length = length1-11-3
        length1 = hex(length1)
        length1 = length1[2:]
        length = hex(length)
        length = length[2:]

        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        crcofhalf =  str(lo)+str(hi)

        # ////////////////////////////////// crc 2 //////////////////////////////

        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1

        datatocrc2 = bytes.fromhex(datatocrc2)
        crcoffull = crc(datatocrc2)

        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))


        crcoffull = str(lo)+str(hi)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1+crcoffull+lasttag
        return frame
    
    except Exception as e:
        print("Error",e)
# -------------------------------------------------------------------------------------------


def instantframing():
    try:
        get_sequence_number(0);
        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(2)
        get_sequence_number(1);
        get_sequence_number(0);
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        hdlc = "E6E600"
        TAG_AARQ = "C0"
        xDlmsRequest1 = "01C1000701005E5B00FF0200" 
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+2+4+4)/2)
        length1 = hex(length1)
        length1 = length1[2:]

        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # print(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # print("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)

        # ////////////////////////////////// crc 2 //////////////////////////////

        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1
        datatocrc2 = bytes.fromhex(datatocrc2)

        crcoffull = crc(datatocrc2)
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))


        crcoffull = str(lo)+str(hi)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+crcoffull+lasttag
        return frame

    except Exception as e:
        print("Error",e)        

def commandframing(obis):
    try:
        get_sequence_number(0);
        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(2)
        get_sequence_number(1);

        get_sequence_number(0);
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]

        hdlc = "E6E600"
        TAG_AARQ = "C0"
        xDlmsRequest1 = obis

        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+2+4+4)/2)
        # print("len ;",(length1))
        length1 = hex(length1)
        length1 = length1[2:]

        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)

        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1

        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))


        crcoffull = str(lo)+str(hi)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+crcoffull+lasttag
        return frame

    except Exception as e:
        print("Error",e)

def loadframing(fromdate,todate):
    try:
        get_sequence_number(0);
        startbit = "7E"
        aarqtag = "A0"
        # length1 = 
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(2)
        get_sequence_number(1);
        get_sequence_number(0);
        # print(ControlField)
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        # print(str(ControlField))
        # ControlField = "323ABD"
        # get_sequence_number(1,g_RRR,g_SSS)
        # datatocrc = 
        hdlc = "E6E600"
        # controlfield
        TAG_AARQ = "C0"
        # length
        xDlmsRequest1 = "01C100070100630100FF02" 
        # 07E80412040B0000 07E80412040D0000
        # data = "01010204020412000809060000010000FF0F02120000090C"+from_year+from_month+from_date+from_day+from_hour+from_minute+from_second+"FF000000090C"+to_year+to_month+to_date+to_day+to_hour+to_minute+to_second+"FF0000000100"
        # crc 
        data = "01010204020412000809060000010000FF0F02120000090C"+fromdate+"FF000000090C"+todate+"FF0000000100"    
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+len(data)+2+4+4)/2)
        # print("len ;",(length1))
        length1 = hex(length1)
        length1 = length1[2:]
        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # print(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # print("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # print(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+data

        # print(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # print("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # print(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # print(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+data+crcoffull+lasttag
        # print(frame)
        return frame

    except Exception as e:
        print("Error",e)

def supervisoryframing():
    try:
        startbit = "7E"
        aarqtag = "A0"
        # length1 = 
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(3);
        # print(ControlField)
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        # print(str(ControlField))
        # ControlField = "323ABD"
        # get_sequence_number(1,g_RRR,g_SSS)
        # datatocrc =    
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+4+2)/2) #crc length 4 added 2 of length1
        # print("len ;",(length1))
        # length1 = hex(length1)
        length1 = f"{length1:02X}"
        # print("0x" + formatted_hex)
        # print(length1)

        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # print(dataforcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # print("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # print(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf

        # print(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # print("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # print(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # print(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+lasttag
        # print(frame)
        return frame

    except Exception as e:
        print("Error",e)        

def specialframing():
    try:

        global special_counter
        startbit = "7E"
        aarqtag = "A0"
        # length1 = 
        serveraddress = "03"
        clientaddress = "41"
        ControlField = get_sequence_number(2)
        get_sequence_number(1);
        # print(ControlField)
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        # print(str(ControlField))
        # ControlField = "323ABD"
        # get_sequence_number(1,g_RRR,g_SSS)
        # datatocrc = 
        hdlc = "E6E600"
        # controlfield
        TAG_AARQ = "C0"
        # length
        dlms = "02C1000000"
        special_counter = special_counter + 1;
        special_counter1 = f"{special_counter:02X}"
        # print(special_counter1)
        # special_counter = special_counter[2:]
        # print(special_counter)
        xDlmsRequest1 =  dlms + str(special_counter1)
        # crc 
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+2+4+4)/2)
        # print("len ;",(length1))
        length1 = hex(length1)
        length1 = length1[2:]
        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # print(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # print("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # print(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1

        # print(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # print("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # print(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # print(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+crcoffull+lasttag
        # print(frame)
        return frame

    except Exception as e:
        print("Error",e)

def serial_write_read(serial_obj,con1):
    try:

        global metertype
        print(type(metertype))
        wait_count = 0
        data_available = False
        response_buffer = [] # Assuming you initialize your response buffer outside this function if needed

        if METER_DEBUG:
            print("RES: ", end='')

        serial_obj.write(con1)

        if(metertype == "LG"):
            time.sleep(1)
        else:
            time.sleep(1)    
        

        while serial_obj.in_waiting >= 0:
            if serial_obj.in_waiting > 0:
                data_available = True
                wait_count = 0
                
                incoming_byte = serial_obj.read(1)
                if incoming_byte == b'\x00':
                    print("Null Received")
                    break
                response_buffer.append(incoming_byte)

                print(incoming_byte.hex(), end=' ')
                #     print(incoming_byte)


            else:
                if wait_count > 5:
                    break
                wait_count += 1

            # if(metertype == "LG"):
            #     print("lg")
                    

            if data_available and serial_obj.in_waiting == 0:
                if serial_obj.in_waiting == 0:
                    break

        # Set DATA_COMMUNICATION LOW
        # digitalWrite(DATA_COMMUNICATION, LOW)
        print("\n")
        # print(response_buffer)
        return response_buffer

    except Exception as e:
        print("Error",e)    

def readConfigurations(serial_obj,parameter,obis):
    try:
        global meterslno
        global final_block,frame_complete,Block_response,from_date_hex,to_date_hex
        final_block = False
        frame_complete = False
        Block_response = False
        # s.settimeout(10)
        # global from_date,to_date
        spaced_string = ""
        try:
            for i in range (3):
                print("MR MODE METER "+parameter)

                # print("MR MODE SNRM ")
                commandforprofile = "7ea0070341935a647e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")
                if(res == 1):

                    # print("MR MODE AARQ ")

                    commandforprofile = aarqframing()
                    # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                    con1 = bytearray.fromhex(commandforprofile)
                    print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"AARQ",0,"") 

                    if(res == 1):
                        global special_counter
                        special_counter = 0
                        commandforprofile = commandframing(obis)
                        # 7E A0 19 03 41 DA 7C D6 E6 E6 00 C0 01 C1 00 01 00 00 60 01 00 FF 02 00 89 A0 7E
                        # 7E A0 1a 03 41 32 f7 98 E6 E6 00 C0 01 C1 00 07 01 00 00 60 01 00 FF 02 00 4c e5 7E
                        con1 = bytearray.fromhex(commandforprofile)
                        print ('PHASE REQUEST = ' + str(commandforprofile)+"\n")
                        meterres = serial_write_read(serial_obj,con1)
                        res = responseparsing(meterres,parameter,0,"") 
                        # finalstring = finalstring + res + "_"
                        if(res == 1):
                            while (frame_complete):
                                integer_value = int(hex_values[1], 16)
                                check_a0 = bit_read((integer_value), 3)

                                if(check_a0 == 0):
                                    commandforprofile = specialframing()
                                else:
                                    commandforprofile = supervisoryframing()  

                                get_sequence_number(0)
                                con1 = bytearray.fromhex(commandforprofile)
                                print ('REQUEST = ' + str(commandforprofile)+"\n")
                                
                                meterres = serial_write_read(serial_obj,con1)
                                res = responseparsing(meterres,"SPECIALDATA",0,"") 
                                integer_value = int(hex_values[1], 16)

                                check_a0 = bit_read((integer_value), 3)

                                if(Block_response == False):
                                    if(check_a0 == 0):
                                        frame_complete = False
                                else:
                                    if(Block_response == True and final_block == False):
                                        print("hiii",len(hex_values))
                                        if(len(hex_values) > 13):
                                            if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                                # print("in")
                                                if(check_a0 == 0):
                                                    frame_complete = False
                                                else:
                                                    final_block = True    
                                    else:
                                        if(final_block == True):

                                            if(check_a0 == 0):
                                                frame_complete = False

                            if(frame_complete == False):
                                print("break")
                                break
                                break


            commandforprofile = "7ea00703415356a27e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"") 
            g_RRR = 0
            g_SSS = 0
            print("----------------------------------------------------------------------------------------------------------------------------------")

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"       

    except Exception as e:
        print("Error",e)

def readEventCount(serial_obj,profile,obis):
    try:
        global meterslno,profilecount
        global final_block,frame_complete,Block_response,from_date_hex,to_date_hex,countofeventsoccured
        final_block = False
        frame_complete = False
        Block_response = False
        profilecount = 0
        # s.settimeout(10)
        # global from_date,to_date
        spaced_string = ""
        try:
            print("MR MODE "+profile+" EVENT COUNT ")

            # print("MR MODE SNRM ")
            commandforprofile = "7ea0070341935a647e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            if(res == 1):

                # print("MR MODE AARQ ")

                commandforprofile = aarqframing()
                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                con1 = bytearray.fromhex(commandforprofile)
                print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"AARQ",0,"") 

                if(res == 1):
                    global special_counter
                    special_counter = 0
                    commandforprofile = commandframing(obis)
                    # 7E A0 19 03 41 DA 7C D6 E6 E6 00 C0 01 C1 00 01 00 00 60 01 00 FF 02 00 89 A0 7E
                    # 7E A0 1a 03 41 32 f7 98 E6 E6 00 C0 01 C1 00 07 01 00 00 60 01 00 FF 02 00 4c e5 7E
                    con1 = bytearray.fromhex(commandforprofile)
                    print ('EVENT COUNT REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"EVENTCOUNT",0,"") 
                    eventcount = countofeventsoccured
                    # finalstring = finalstring + res + "_"
                    if(res == 1):

                        while (frame_complete):
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(check_a0 == 0):
                                commandforprofile = specialframing()
                            else:
                                # print("in supervisoryframing")
                                commandforprofile = supervisoryframing()     
                                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                            get_sequence_number(0)
                            con1 = bytearray.fromhex(commandforprofile)
                            print ('REQUEST = ' + str(commandforprofile)+"\n")
                            
                            
                            meterres = serial_write_read(serial_obj,con1)
                            res = responseparsing(meterres,"SPECIALDATA",0,"") 
                            # print(res)
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(Block_response == False):
                                if(check_a0 == 0):
                                    frame_complete = False
                            else:
                                if(Block_response == True and final_block == False):
                                    print("hiii",len(hex_values))
                                    if(len(hex_values) > 13):
                                        if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                            # print("in")
                                            if(check_a0 == 0):
                                                frame_complete = False
                                            else:
                                                final_block = True    
                                else:
                                    if(final_block == True):

                                        if(check_a0 == 0):
                                            frame_complete = False

                    
                    # print("MR MODE DISCONNECT ")

                commandforprofile = "7ea00703415356a27e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                print("----------------------------------------------------------------------------------------------------------------------------------")
                # spaced_string = ' '.join(spaced_string[i:i+2] for i in range(0, len(spaced_string), 2))
                return eventcount    

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"  

    except Exception as e:
        print("Error",e)

def readLoadProfileReading(serial_obj):
    try:
        global finalstring ,profilename
        global final_block,frame_complete,Block_response,from_date_hex,to_date_hex,LoadStatus
        global from_date_hex,to_date_hex
        finalstring = ""
        final_block = False
        frame_complete = False
        Block_response = False
        # s.settimeout(10)
        # global from_date,to_date
        spaced_string = ""
        instataneousres = ""
        profilename = "L" 
        try:
            print("MR MODE LOAD_PROFILE ")

            commandforprofile = "7ea0070341935a647e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            if(res == 1):


                commandforprofile = aarqframing()
                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                con1 = bytearray.fromhex(commandforprofile)
                print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"AARQ",0,"") 

                if(res == 1):
                    global special_counter
                    special_counter = 0
                    # commandforprofile = loadframing("07E8041404050000","07E80414040A3B00")

                    commandforprofile = loadframing(from_date_hex,to_date_hex)
                    con1 = bytearray.fromhex(commandforprofile)
                    print ('LOAD PROFILE REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"DATA",0,"") 
                    if(res == 1):
                        while (frame_complete):
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(check_a0 == 0):
                                commandforprofile = specialframing()
                            else:
                                # print("in supervisoryframing")
                                commandforprofile = supervisoryframing()     
                                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                            get_sequence_number(0)
                            con1 = bytearray.fromhex(commandforprofile)
                            print ('REQUEST = ' + str(commandforprofile)+"\n")
                            
                            
                            meterres = serial_write_read(serial_obj,con1)
                            res = responseparsing(meterres,"SPECIALDATA",0,"") 
                            # print(res)
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(Block_response == False):
                                if(check_a0 == 0):
                                    frame_complete = False
                            else:
                                if(Block_response == True and final_block == False):
                                    print("hiii",len(hex_values))
                                    if(len(hex_values) > 13):
                                        if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                            # print("in")
                                            if(check_a0 == 0):
                                                frame_complete = False
                                            else:
                                                final_block = True    
                                else:
                                    if(final_block == True):

                                        if(check_a0 == 0):
                                            frame_complete = False
                        
                        LoadStatus = 1
                    
                    # print("MR MODE DISCONNECT ")

            commandforprofile = "7ea00703415356a27e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"") 
            print("----------------------------------------------------------------------------------------------------------------------------------")
            data = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+finalstring[0:len(finalstring)-1]+"$"  
            todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/L.log"
            append_to_file(todayDate1,data)   
            append_to_file(todayDate,data)   

            return data
            g_RRR = 0
            g_SSS = 0

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"  

    except Exception as e:
        print("Error",e)

def finaldataframing(data):
    spaced_string = ' '.join(intdata[i:i+2] for i in range(0, len(data), 2))
    finalstring = finalstring + spaced_string
    print(finalstring)

def get_response_as_string():
    # Join all byte segments and decode to form the final string
    return b''.join(response_buffer).decode('ascii', errors='replace')


def readInstantData(serial_obj):
    try:
        global finalstring ,profilename
        finalstring = ""
        profilename = "IP"
        # s.settimeout(10)
        spaced_string = ""
        instataneousres = ""
        global final_block,frame_complete,Block_response
        final_block = False
        frame_complete = False
        Block_response = False    
        try:
            print("MR MODE INSTANTANEOUS ")

            commandforprofile = "7ea0070341935a647e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            if(res == 1):


                commandforprofile = aarqframing()
                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                con1 = bytearray.fromhex(commandforprofile)
                print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"AARQ",0,"") 

                if(res == 1):
                    global special_counter
                    special_counter = 0
                    commandforprofile = instantframing()
                    con1 = bytearray.fromhex(commandforprofile)
                    print ('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"DATA",0,"") 

                    if(res == 1):

                        while (frame_complete):
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(check_a0 == 0):
                                commandforprofile = specialframing()
                            else:
                                # print("in supervisoryframing")
                                commandforprofile = supervisoryframing()     
                                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                            get_sequence_number(0)
                            con1 = bytearray.fromhex(commandforprofile)
                            print ('REQUEST = ' + str(commandforprofile)+"\n")
                            
                            
                            meterres = serial_write_read(serial_obj,con1)
                            res = responseparsing(meterres,"SPECIALDATA",0,"") 
                            # print(res)
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(Block_response == False):
                                if(check_a0 == 0):
                                    frame_complete = False
                            else:
                                if(Block_response == True and final_block == False):
                                    print("hiii",len(hex_values))
                                    if(len(hex_values) > 13):
                                        if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                            # print("in")
                                            if(check_a0 == 0):
                                                frame_complete = False
                                            else:
                                                final_block = True    
                                else:
                                    if(final_block == True):

                                        if(check_a0 == 0):
                                            frame_complete = False
                    
                    # print("MR MODE DISCONNECT ")

                commandforprofile = "7ea00703415356a27e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")
                print("----------------------------------------------------------------------------------------------------------------------------------")
                data = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+finalstring[0:len(finalstring)-1]+"$"  
                todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/IP.log"
                append_to_file(todayDate1,data)   
                append_to_file(todayDate,data)   

                g_RRR = 0
                g_SSS = 0
                return data

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"     

    except Exception as e:
        print("Error",e)

def readSclarObisValues(serial_obj,profilename,obis):
    try:
        global finalstring
        global final_block,frame_complete,Block_response

        finalstring = ""
        final_block = False
        frame_complete = False
        Block_response = False
        # s.settimeout(10)
        spaced_string = ""
        instataneousres = ""

        try:

            for i in range (3):
                print("MR MODE "+profilename)

                commandforprofile = "7ea0070341935a647e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")
                if(res == 1):


                    commandforprofile = aarqframing()
                    # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                    con1 = bytearray.fromhex(commandforprofile)
                    print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"AARQ",0,"") 

                    if(res == 1):
                        global special_counter
                        special_counter = 0
                        commandforprofile = commandframing(obis)
                        con1 = bytearray.fromhex(commandforprofile)
                        print ('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                        
                        
                        meterres = serial_write_read(serial_obj,con1)
                        res = responseparsing(meterres,"DATA",0,"") 

                        if(res == 1):

                            while (frame_complete):
                                integer_value = int(hex_values[1], 16)
                                # Convert integer to binary string, remove '0b' prefix
                                #binary_string = bin(integer_value)
                                # #binary_string = bin(integer_value)
                                #print(type(binary_string))
                                check_a0 = bit_read((integer_value), 3)

                                if(check_a0 == 0):
                                    commandforprofile = specialframing()
                                else:
                                    # print("in supervisoryframing")
                                    commandforprofile = supervisoryframing()     
                                    # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                                get_sequence_number(0)
                                con1 = bytearray.fromhex(commandforprofile)
                                print ('REQUEST = ' + str(commandforprofile)+"\n")
                                
                                meterres = serial_write_read(serial_obj,con1)
                                res = responseparsing(meterres,"SPECIALDATA",0,"") 
                                # print(res)
                                integer_value = int(hex_values[1], 16)
                                # Convert integer to binary string, remove '0b' prefix
                                #binary_string = bin(integer_value)
                                # #binary_string = bin(integer_value)
                                #print(type(binary_string))
                                check_a0 = bit_read((integer_value), 3)

                                if(Block_response == False):
                                    if(check_a0 == 0):
                                        frame_complete = False
                                else:
                                    if(Block_response == True and final_block == False):
                                        print("hiii",len(hex_values))
                                        if(len(hex_values) > 13):
                                            if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                                print("in")
                                                if(check_a0 == 0):
                                                    frame_complete = False
                                                else:
                                                    final_block = True    
                                    else:
                                        if(final_block == True):

                                            if(check_a0 == 0):
                                                frame_complete = False
                            break
                    # print("MR MODE DISCONNECT ")

            commandforprofile = "7ea00703415356a27e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            print("----------------------------------------------------------------------------------------------------------------------------------")
            data = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+finalstring[0:len(finalstring)-1]+"$"  
            todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/"+meterslno+"_config_files.log"
            append_to_file(todayDate1,data)
            append_to_file(todayDate,data)  
            g_RRR = 0
            g_SSS = 0
            return data

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"     

    except Exception as e:
        print("Error",e)

def readBillingData(serial_obj):
    try:
        global finalstring ,profilename,fromentry,toentry,entry
        finalstring = ""
        profilename = "B"
        # s.settimeout(10)
        # global from_date,to_date
        spaced_string = ""
        instataneousres = ""
        global final_block,frame_complete,Block_response
        final_block = False
        frame_complete = False
        Block_response = False    
        try:
            print("MR MODE BILLING_PROFILE ")

            # print("MR MODE SNRM ")
            commandforprofile = "7ea0070341935a647e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            if(res == 1):

                # print("MR MODE AARQ ")

                commandforprofile = aarqframing()
                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                con1 = bytearray.fromhex(commandforprofile)
                print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"AARQ",0,"") 

                if(res == 1):
                    global special_counter
                    special_counter = 0
                    if(entry == "1"):
                        print("in On_Demand")
                        availableentry = format(int(fromentry), '02x')
                        entriestoberead = format(int(toentry), '02x')
                        # availableentry = "06"
                        # entriestoberead = "07"
                        ondemandframe = "0102020406000000"+availableentry+"06000000"+entriestoberead+"120001120000"
                        commandforprofile = commandframing("01C100070100620100FF02"+ondemandframe)
                    else:
                        print("read all")
                        commandforprofile = commandframing("01C100070100620100FF0200")

                    con1 = bytearray.fromhex(commandforprofile)
                    print ('BILLING REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"DATA",0,"") 
                    # finalstring = finalstring + res + "_"
                    if(res == 1):

                        while (frame_complete):
                            print(hex_values[1])

                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            # print((binary_string))
                            check_a0 = bit_read((integer_value), 3)
                            print(check_a0)
                            if(check_a0 == 0):
                                commandforprofile = specialframing()
                            else:
                                # print("in supervisoryframing")
                                commandforprofile = supervisoryframing()     
                                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                            get_sequence_number(0)
                            con1 = bytearray.fromhex(commandforprofile)
                            print ('REQUEST = ' + str(commandforprofile)+"\n")
                            
                            
                            meterres = serial_write_read(serial_obj,con1)
                            res = responseparsing(meterres,"SPECIALDATA",0,"") 
                            print(hex_values[1])
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            # #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)
                            # print("aa",check_a0)
                            if(Block_response == False):
                                if(check_a0 == 0):
                                    frame_complete = False
                            else:
                                if(Block_response == True and final_block == False):
                                    print("hiii",len(hex_values))
                                    if(len(hex_values) > 13):
                                        if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                            # print("in")
                                            if(check_a0 == 0):
                                                frame_complete = False
                                            else:
                                                final_block = True    
                                else:
                                    if(final_block == True):

                                        if(check_a0 == 0):
                                            frame_complete = False

                    
                    # print("MR MODE DISCONNECT ")

                commandforprofile = "7ea00703415356a27e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                print("----------------------------------------------------------------------------------------------------------------------------------")
                data = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+finalstring[0:len(finalstring)-1]+"$"  
                todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/"+meterslno+"_billing.log"
                append_to_file(todayDate1,data)
                append_to_file(todayDate,data)  

                return data

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"              

    except Exception as e:
        print("Error",e)

def readEventsProfile(serial_obj,profilename,obis,profilecount):
    try:
        global finalstring 
        finalstring = ""
        # s.settimeout(10)
        # global from_date,to_date
        spaced_string = ""
        instataneousres = ""
        global final_block,frame_complete,Block_response
        final_block = False
        frame_complete = False
        Block_response = False    
        try:
            print("MR MODE",profilename," PROFILE ")

            # print("MR MODE SNRM ")
            commandforprofile = "7ea0070341935a647e"
            con1 = bytearray.fromhex(commandforprofile)
            print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
            
            
            meterres = serial_write_read(serial_obj,con1)
            res = responseparsing(meterres,"SNRM",0,"")
            if(res == 1):

                # print("MR MODE AARQ ")

                commandforprofile = aarqframing()
                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                con1 = bytearray.fromhex(commandforprofile)
                print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"AARQ",0,"") 

                if(res == 1):
                    global special_counter
                    special_counter = 0
                    # if(On_Demand == 1)
                    # commandforprofile = commandframing("01C100070100620100FF0200")
                    # else:
                    #     commandforprofile = commandframing("01C100070100620100FF0200","On_Demand")
                    print(profilecount)
                    if(profilecount > 5):
                        profilecountfrom = format(int(profilecount-5), '02x')

                    else:
                        profilecountfrom = "01"
                    profilecount = format((profilecount), '02x')
        
                    eventspraming = "0102020406000000"+profilecountfrom+"06000000"+profilecount+"120001120000"
                    commandforprofile = commandframing(obis+eventspraming)
                    con1 = bytearray.fromhex(commandforprofile)
                    print ('EVENTS REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"DATA",0,"") 
                    # finalstring = finalstring + res + "_"
                    if(res == 1):

                        while (frame_complete):
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(check_a0 == 0):
                                commandforprofile = specialframing()
                            else:
                                # print("in supervisoryframing")
                                commandforprofile = supervisoryframing()     
                                # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"
                            get_sequence_number(0)
                            con1 = bytearray.fromhex(commandforprofile)
                            print ('REQUEST = ' + str(commandforprofile)+"\n")
                            
                            
                            meterres = serial_write_read(serial_obj,con1)
                            res = responseparsing(meterres,"SPECIALDATA",0,"") 
                            # print(res)
                            integer_value = int(hex_values[1], 16)
                            # Convert integer to binary string, remove '0b' prefix
                            #binary_string = bin(integer_value)
                            # #binary_string = bin(integer_value)
                            #print(type(binary_string))
                            check_a0 = bit_read((integer_value), 3)

                            if(Block_response == False):
                                if(check_a0 == 0):
                                    frame_complete = False
                            else:
                                if(Block_response == True and final_block == False):
                                    print("hiii",len(hex_values))
                                    if(len(hex_values) > 13):
                                        if(hex_values[13] == "c1" and hex_values[14] == "01"):
                                            # print("in")
                                            if(check_a0 == 0):
                                                frame_complete = False
                                            else:
                                                final_block = True    
                                else:
                                    if(final_block == True):

                                        if(check_a0 == 0):
                                            frame_complete = False

                    
                    # print("MR MODE DISCONNECT ")

                commandforprofile = "7ea00703415356a27e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                print("----------------------------------------------------------------------------------------------------------------------------------")
                data = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+finalstring[0:len(finalstring)-1]+"$" 
                todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/"+meterslno+"_config_files.log"

                append_to_file(todayDate1,data)
                append_to_file(todayDate,data)   

                return data

        except socket.timeout:
            print("Energy Meter Response Not Recieved")
            return "Null"              
    
    except Exception as e:
        print("Error",e)

def responseparsing(response,flag,iv1,profiletype):
    try:
        global hex_values,meterslno,countofeventsoccured,PhaseType,g_year,g_month,g_day,g_minutes,g_seconds,g_startingHour,lct,drift
        hex_values = [f"{b[0]:02x}" for b in response] 
        global frame_complete 
        global Block_response 
        status = 1
        # print(str(response))
        if(hex_values == []):
            print("empty")
            status = 0
            return status

        if(flag == "SNRM"):
            if(hex_values[0] == "7e"):
                status = 1


        elif(flag == "AARQ"):
            if(len(hex_values) > 20):
                if (hex_values[25] ==  "03" and hex_values[26] ==  "02" and
                    hex_values[27] ==  "01" and hex_values[28] ==  "00") or \
                   (hex_values[29] ==  "03" and hex_values[30] ==  "02" and
                    hex_values[31] ==  "01" and hex_values_buffer[32] ==  00):
                    print("METER AARQ SUCCESS")
                    status = 1
                else:
                    print("METER AARQ FAILURE")
                    status = 0


        elif(flag == "DATA"):
            if (hex_values[0] ==  "7e" or hex_values[2] != "00"):
                hex_list_to_string(hex_values)

                if (hex_values[11] ==  "c4"):   
                    if (hex_values[12] ==  "02" ):
                        Block_response = True
                    else:
                        if(hex_values[12] ==  "01" ):
                           Block_response = False 
                
                # print(hex_values[1])
                integer_value = int(hex_values[1], 16)
                # Convert integer to binary string, remove '0b' prefix
                #binary_string = bin(integer_value)
                # #binary_string = bin(integer_value)
                #print(type(binary_string))
                segment_action = bit_read((integer_value), 3)
                print("this is a segment",segment_action)
                if (Block_response == False and segment_action ==  0):  
                   frame_complete = False
                else:
                    if(Block_response == True and segment_action ==  0 and hex_values[14] == "01" ):

                        frame_complete = False

                    else:
                        if(Block_response == True and segment_action ==  1 and hex_values[14] == "00" ):

                            frame_complete = True

                        else:   

                            frame_complete = True        

            else:
                status = 0

        elif(flag == "METERNO"):
            # Initialize variables
            ParsedMeterSerialNo = 0
            MeterSerialNo_Final = ""
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15
            # Check if the value at ResponseBuffer[resIndex][startColumnIndex] is 0x06
            for resColumnIndex in range(startColumnIndex, count):
                if hex_values[15] == "06" or hex_values[15] == "07":
                    ParsedMeterSerialNo = (ParsedMeterSerialNo << 8) | int(hex_values[resColumnIndex],16)
                    MeterSerialNo_Final = MeterSerialNo_Final  + str(ParsedMeterSerialNo)

                elif hex_values[startColumnIndex] in ("09", "0a" , "0A") and resColumnIndex >= (startColumnIndex + 2):
                    MeterSerialNo_Final = MeterSerialNo_Final + str(hex_values[resColumnIndex])                            

            meterslno = bytes.fromhex(MeterSerialNo_Final).decode('utf-8')
            meterslno = meterslno.strip()
            print("Meter Number is : ",meterslno)
            write_to_file("E:/home/lpu/KPTCL_rs485/config/meterslno_"+gwid,meterslno)

            status = 1

        elif(flag == "EVENTCOUNT"):
            ProfileVEBytes = "0"
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15
            for resColumnIndex in range(startColumnIndex, count):
                if(flag == "EVENTCOUNT" and resColumnIndex >= (startColumnIndex + 1)):
                    ProfileVEBytes = ProfileVEBytes + str(hex_values[resColumnIndex]);
            
            countofeventsoccured = int((ProfileVEBytes),16)
            print("ProfileVEBytes is : ",countofeventsoccured)

        elif(flag == "SPECIALDATA"):
            # print("special1") 
            # print(hex_values[1])
            if(hex_values[0] == "7e" and hex_values[1] == "a0"):
                # print("special")
                status = 1 
                # hex_values[13] = specialres[1]
                # hex_values[14] = specialres[2]
            hex_list_to_string(hex_values)

        elif(flag == "PHASE"):
            # print("special1") 
            # print(hex_values[1])
            if(hex_values[15] == "11"):
                startColumnIndex = 16
            else:
                startColumnIndex = 17
            
            MeterCategoryType = hex_values[startColumnIndex];
            
            if(MeterCategoryType == "5" or MeterCategoryType == "6"):
                PhaseType = 1
                status = 1

            else:
                PhaseType = 3
                status = 1

            
            print("the phase type is ",PhaseType)
            
           
        elif(flag == "RTC"):
            if (hex_values[0] ==  "7e" or hex_values[2] != "00"):
                # print("special1") 
                # print(hex_values[1])
                startRowIndex = 17;
                g_year = (int)(int(hex_values[startRowIndex],16) << 8 | int(hex_values[startRowIndex + 1],16));
                g_month = (int(hex_values[startRowIndex+2],16));
                g_day = (int(hex_values[startRowIndex+3],16));
                g_startingHour = int(hex_values[startRowIndex+5],16);
                g_minutes = int(hex_values[startRowIndex+6],16);
                g_seconds = int(hex_values[startRowIndex+7],16);

                print("Meter RTC IS "+str(g_year)+" "+str(g_month)+" "+str(g_day)+" "+str(g_startingHour)+" "+str(g_minutes)+" "+str(g_seconds))

        elif(flag == "LCT"):
                    # Initialize variables
            print("vaish")
            index = 0
            ddoublelongvalue= 0
            kWh_finalvalue = 0
            kWh_floatvalue = 0
            lct = ""
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15
            # Check if the value at ResponseBuffer[resIndex][startColumnIndex] is 0x06
            for resColumnIndex in range(startColumnIndex, count):
                if hex_values[startColumnIndex] in ("09", "0A") and resColumnIndex >= (startColumnIndex + 2):
                    lct = str(lct)  + str(hex_values[resColumnIndex]) 
                    lct = int(lct,16)

                elif(hex_values[startColumnIndex] == "05" or hex_values[startColumnIndex] == "06"):
                    print("hii")
                    while (startColumnIndex < (count-1)):

                        startColumnIndex = startColumnIndex+1
                        # print(hex_values[startColumnIndex])
                        ddoublelongvalue = (ddoublelongvalue << 8) | int(hex_values[startColumnIndex],16)
                        # print(ddoublelongvalue)
                    lct = str(ddoublelongvalue)
                elif (hex_values[startColumnIndex] == "12"):
                    while (startColumnIndex < (count-1)):
                        startColumnIndex = startColumnIndex+1

                        ddoublelongvalue = (ddoublelongvalue << 8) | int(hex_values[startColumnIndex],16);
                    lct = str(ddoublelongvalue)


            print("The Load Captured Time is : "+str(lct))                       

        return status        

    except Exception as e:
        print("Error",e)

def ReadObis(serial_obj):
    try:
        data = ""
        ipobpacket = readSclarObisValues(serial_obj,"IPOB","01C1000701005E5B00FF0300")   #InstantdataObis 0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x03, 0x00
        isobpacket = readSclarObisValues(serial_obj,"ISOB","01C1000701005E5B03FF0300")   #Instantobisscalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x03, 0x00
        lpobpacket = readSclarObisValues(serial_obj,"LPOB","01C100070100630100FF0300")   #LoaddataObis 0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x03, 0x00
        lsobpacket = readSclarObisValues(serial_obj,"LSOB","01C1000701005E5B04FF0300")   #Loadobisscalar 0x07, 0x01, 0x00, 94, 91, 0x04, 0xFF, 0x03, 0x00
        bobpacket  = readSclarObisValues(serial_obj,"BOB","01C100070100620100FF0300")   #BillingdataObis 0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x03, 0x00
        bsobpacket = readSclarObisValues(serial_obj,"BSOB","01C1000701005E5B06FF0300")   #Billingobisscalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x03, 0x00
        eobpacket  = readSclarObisValues(serial_obj,"EOB","01C100070000636201FF0300")   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
        esobpacket = readSclarObisValues(serial_obj,"ESOB","01C1000701005E5B07FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
        dsobpacket = readSclarObisValues(serial_obj,"DSOB","01C1000701005E5B05FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
        dlobpacket = readSclarObisValues(serial_obj,"DLOB","01C100070100630200FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00

        data = ipobpacket+isobpacket+lpobpacket+lsobpacket+bsobpacket+bobpacket+esobpacket+eobpacket+dsobpacket+dlobpacket
        
        MSTLOG(data)    

        return data

    except Exception as e:
        print(e)
        return "0,0"  

def ReadScalar(serial_obj):
    try:
        ipsvpacket = readSclarObisValues(serial_obj,"IPSV","01C1000701005E5B03FF0200")   #InstantScalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x02, 0x00
        lpsvpacket = readSclarObisValues(serial_obj,"LPSV","01C1000701005E5B04FF0200")   #LoadScalar 0x07, 0x01, 0x00, 94, 0x5B, 0x04, 0xFF, 0x02, 0x00
        bsvpacket  = readSclarObisValues(serial_obj,"BSV","01C1000701005E5B06FF0200")   #BillingScalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x02
        esvpacket  = readSclarObisValues(serial_obj,"ESV","01C1000701005E5B07FF0200")   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
        dlsvpacket = readSclarObisValues(serial_obj,"DLSV","01C1000701005E5B05FF0200")   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00

        data = ipsvpacket+lpsvpacket+bsvpacket+esvpacket+dlsvpacket
        
        MSTLOG(data)    

        return data

    except Exception as e:
        print(e)
        return "Null"  


# ----------------------------------------------------AUTOMATION------------------------------------------------ 

def readProfilesForConfigurations(serial_obj):
    try:

        global configflag,ippacket,ipsvpacket,ipobpacket,isobpacket,lpsvpacket,lpobpacket,lsobpacket,bsvpacket,bobpacket,bsobpacket,esvpacket,eobpacket,esobpacket

        # /////////////////////////////////////////////////instant configurations/////////////////////////////////////////////////////////////////////
        
        if(configflag == 0):

        # ///////////////////////////////////////////////////ip configurations//////////////////////////////////////////////////////////////////////

            if(ipsv == 0):
                
                ipsvpacket= readSclarObisValues(serial_obj,"IPSV","01C1000701005E5B03FF0200")   #InstantScalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x02, 0x00

            if(ipob == 0):    
                
                ipobpacket= readSclarObisValues(serial_obj,"IPOB","01C1000701005E5B00FF0300")   #InstantdataObis 0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x03, 0x00

            if(isob == 0):    
                
                isobpacket= readSclarObisValues(serial_obj,"ISOB","01C1000701005E5B03FF0300")   #Instantobisscalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x03, 0x00

        # # ///////////////////////////////////////////////////load configurations//////////////////////////////////////////////////////////////////////

            if(lpsv == 0):    
                
                lpsvpacket= readSclarObisValues(serial_obj,"LPSV","01C1000701005E5B04FF0200")   #LoadScalar 0x07, 0x01, 0x00, 94, 0x5B, 0x04, 0xFF, 0x02, 0x00
            
            if(lpob == 0):

                lpobpacket= readSclarObisValues(serial_obj,"LPOB","01C100070100630100FF0300")   #LoaddataObis 0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x03, 0x00
            
            if(lsob == 0):    

                lsobpacket= readSclarObisValues(serial_obj,"LSOB","01C1000701005E5B04FF0300")   #Loadobisscalar 0x07, 0x01, 0x00, 94, 91, 0x04, 0xFF, 0x03, 0x00

        # # ////////////////////////////////////////////////////billing configurations/////////////////////////////////////////////////////////////////////


            if(bsv == 0):    
                
                bsvpacket= readSclarObisValues(serial_obj,"BSV","01C1000701005E5B06FF0200")   #BillingScalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x02

            if(bob == 0):        
                
                bobpacket= readSclarObisValues(serial_obj,"BOB","01C100070100620100FF0300")   #BillingdataObis 0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x03, 0x00

            if(bsob == 0):  

                bsobpacket= readSclarObisValues(serial_obj,"BSOB","01C1000701005E5B06FF0300")   #Billingobisscalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x03, 0x00
            

        # # ////////////////////////////////////////////////////events configurations/////////////////////////////////////////////////////////////////////
           
            if(esv == 0):  

                esvpacket= readSclarObisValues(serial_obj,"ESV","01C1000701005E5B07FF0200")   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
            
            if(eob == 0):  
            
                eobpacket= readSclarObisValues(serial_obj,"EOB","01C100070000636201FF0300")   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
            
            if(esob == 0):  
                
                esobpacket= readSclarObisValues(serial_obj,"ESOB","01C1000701005E5B07FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00

        # ////////////////////////////////////////////////////billing configurations/////////////////////////////////////////////////////////////////////


            dsvpacket= readSclarObisValues(serial_obj,"DLSV","01C1000701005E5B05FF0200")   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
            dsobpacket= readSclarObisValues(serial_obj,"DSOB","01C1000701005E5B05FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
            dobpacket= readSclarObisValues(serial_obj,"DLOB","01C100070100630200FF0300")   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00

        data = ipsvpacket+ipobpacket+isobpacket+lpsvpacket+lpobpacket+lsobpacket+bsvpacket+bsobpacket+bobpacket+esvpacket+esobpacket+eobpacket+dsvpacket+dsobpacket+dobpacket
        
        print(data)    

        return data

    except Exception as e:
        print("Error",e)

def ReadLoadProfile(serial_obj):
    try:
        l = "0"
        global LoadStatus
        resp = redis_client1.hget(meterslno+"_time","fromdate")
        print(resp)
        # if(resp.decode('utf-8')
        # resp = "None"
        day = "00"
        fromdate = ""
        todate =""
        datefrom = ""
        loadreadflag = 0
        # print(type(resp))
        if((resp) == None):
            ist_time = datetime.now(ist)
            datefrom = str(ist_time.strftime('%Y-%m-%d'))
            fromdate = datefrom + "-"+day + "-00-00-00"
            # print(fromdate)
        else:
            fromdate = resp.decode('utf-8') 
    # -------------------------------------------------------------------------------------------------------------------
        
        split_strings = fromdate.split('-')

        fromdatefordiff = str(split_strings[0])+"-"+str(split_strings[1])+"-"+str(split_strings[2])+"-"+str(split_strings[4])+"-"+str(split_strings[5])+"-"+str(split_strings[6]) #2024-07-06
        todatefordiff = str(g_year)+"-"+str(g_month)+"-"+str(g_day)+"-"+str(g_startingHour)+"-"+str(g_minutes)+"-"+str(g_seconds)
    # -------------------------------------------------------------------------------------------------------------------
        date_format = "%Y-%m-%d-%H-%M-%S"

        diff1 = datetime.strptime(str(fromdatefordiff), date_format)
        diff2 = datetime.strptime(todatefordiff, date_format)
    # -------------------------------------------------------------------------------------------------------------------
        date_difference = diff2 - diff1
        total_seconds = date_difference.total_seconds()
        print(total_seconds)
    # ---------------------------------------------------------------------------------------------------------------------


        todate = str(g_year)+"-"+str(g_month)+"-"+str(g_day)+"-"+day+"-"+str(g_startingHour)+"-"+str(g_minutes)+"-"+str(g_seconds)
        loaddatetime = fromdate+","+todate
        print("From date is "+fromdate)
        print("To date is "+todate)
    # --------------------------------------------------------------------------------------------------------------------------

    # if(lct == 900 ):
        # print(lct)
        if(total_seconds > int(lct)):
            

        # elif(lct == 1800):
        #     print("in 1800")

        #     if(total_seconds > 1800):
        #         print("in 30")
        #         loadreadflag = 1 

            split_strings = loaddatetime.split(',')
            status = checkdata(split_strings)

            if(status == 1):
                print("j")
                for i in range (3):
                    l = readLoadProfileReading(serial_obj) 
                    if(LoadStatus == 1):
                        print("load done")
                        redis_client1.hset(meterslno+"_time","fromdate",todate)
                        break;
        else:
            print("Load Profile Reading Time is Not Reached")

        return l

    except Exception as e:
        print("Error",e)


def MSTLOG(resp):
    global debug
    if(debug == 1):
        print(resp)

def readBillingProfile(serial_obj):
    try:
        billingflag = 0
        b = "Null"
        ist_time = datetime.now(ist)
        presenttime = str(ist_time.strftime('%d')) 
        MSTLOG(presenttime)
        # time = None
        time = redis_client1.hget(meterslno+"_billing","billingday")
        MSTLOG(time)
        readoncebill = redis_client1.hget(meterslno+"_billing","readonceflag")
        # readoncebill = None
        MSTLOG(readoncebill)
        if((time) == None):
            billingflag = 1
        else:
            MSTLOG(presenttime)
            MSTLOG((time.decode('utf-8')))

            if((readoncebill) == None):
                readoncebill = "0"
                print(readoncebill)
            else:
                readoncebill = readoncebill.decode('utf-8')  

            if(((time).decode('utf-8') != str(presenttime) and readoncebill != "1" and g_startingHour == 1) or readoncebill == "0"):
                print("in")
                billingflag = 1    

        if(billingflag == 1):
            b = readBillingData(serial_obj)
            if(len(b) > 5):
                print("billing")
                redis_client1.hset(meterslno+"_billing","readonceflag",1)

                redis_client1.hset(meterslno+"_billing","billingday",str(presenttime))

        return b

    except Exception as e:
        print("Error",e)

def autodetection(serial_obj):
    try:
        global LLS_Keys,metertype
        print((passwordsofmeter[0]))
        print("AUTO DETECTION")
        autodetectionflag = 0
        for i in range (3):
            for i in range (len(passwordsofmeter)): 
                commandforprofile = "7ea0070341935a647e"
                con1 = bytearray.fromhex(commandforprofile)
                print ('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                meterres = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")
                if(res == 1):

                    
                    print(passwordsofmeter[i]) 
                    LLS_Keys = passwordsofmeter[i]  
                    commandforprofile = aarqframing()
                    # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                    con1 = bytearray.fromhex(commandforprofile)
                    print ('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                    meterres = serial_write_read(serial_obj,con1)
                    res = responseparsing(meterres,"AARQ",0,"") 

                    if(res == 1):
                        autodetectionflag = 1
                        print(meters[i])
                        metertype = str(meters[i])
                        break

            if(autodetectionflag == 1):
                break            

                
        commandforprofile = "7ea00703415356a27e"
        con1 = bytearray.fromhex(commandforprofile)
        print ('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")

        meterres = serial_write_read(serial_obj,con1)
        res = responseparsing(meterres,"SNRM",0,"")     
        print("================================================================================================================================")
        return autodetectionflag

    except Exception as e:
        print("Error",e)

def assignRedisVariables():
    global g_startingHour
    try:

        presenttime = str(ist_time.strftime('%d')) 
        time = redis_client1.hget(meterslno+"_billing","billingday")
        # time = None
        MSTLOG(type(time))

        if((time) != None):
            if((time).decode('utf-8') != str(presenttime) and g_startingHour == 1):
                redis_client1.hset(meterslno+"_billing","readonceflag",1)
                redis_client1.hset(meterslno+"_config","readonceflag",1)
                print("hh")

        readonceconfig = redis_client1.hget(meterslno+"_config","readonceflag")

        # readonceconfig = None
        if((readonceconfig) == None):
           readonceconfig = "0"
           print("hii")
        else:
           readonceconfig = readonceconfig.decode('utf-8')
        
        return readonceconfig

    except Exception as e:
        print(e)



def readAllProfiles(serial_obj):
    try:
        configfiles = "0"
        ippacket ="0"
        loadpacket = "0"
        events = "0"
        b = "0"
        readConfigurations(serial_obj,"PHASE","01C1000100005E5B09FF0200")
        print(datetime.now())
        readConfigurations(serial_obj,"RTC","01C100080000010000FF0200")   # char INST_Obiscode1[] = {0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0xFF, 0x02};
        readConfigurations(serial_obj,"LCT","01C100010100000804FF0200")   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
        readonceconfig = assignRedisVariables()

        if((g_startingHour == 8 and readonceconfig != "1") or readonceconfig == "0"):
            

            configfiles = readProfilesForConfigurations(serial_obj)

            dlpacket = readSclarObisValues(serial_obj,"DL","01C100070100630200FF0200") 

            events = ReadEventsprofilewithcount(serial_obj)   
                                            #EventData
            redis_client1.hset(meterslno+"_config","readonceflag",1)   
        

        ippacket =  readInstantData(serial_obj) #InstantData
        loadpacket = ReadLoadProfile(serial_obj)

        b = readBillingProfile(serial_obj)                                   #BillingData

    except Exception as e:
        print(e)

# ---------------------------------------------------------------------------------------------------------------------------------------------

def hex_list_to_string(hex_list):
    # Join the hexadecimal values together
    global finalstring
    hex_string = ''.join(hex_list)
    spaced_string = ' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))
    finalstring = finalstring + spaced_string + "_"
    # print(finalstring)
    return finalstring

def postdata(finalres):
    print("finalres")
    timeout_seconds = 10

    try:
        # Make the POST request
        url = 'http://localhost:9933/meterdata'

        security_key = "tl2CxESUsQsQNNspCY4GHw"

        # Headers with security key
        headers = {
            "secretkey": security_key,
            "authkey" : "MNFyzLF12Ssf43lW"
        }

        # Send the POST request with security key
        response = requests.post(url, json=finalres, headers=headers)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("POST request successful")
            # data = json.loads(response.text)
            print(response.text)
            # Iterate over each dictionary in the list
            # for entry in data:
            #     for key, value in entry.items():
            #         print(f"{key}: {value}")
            #     print()  # Print an empty line between entries
        else:
            print(f"POST request failed with status code: {response.status_code}")
    except requests.exceptions.Timeout:
        print("Request timed out")

    except requests.exceptions.RequestException as e:
        # Handle exceptions related to the request
        print("Error making POST request:",e)


def checkdata(split_strings):
    from_date = (split_strings[0])
    to_date = (split_strings[1])


    global from_date_hex,to_date_hex
    # Example number
    # number = "2024_04_24_11_"+meterindex+"_00"

    # Convert to hexadecimal
    from_date_hex = convert_to_hex(from_date)
    to_date_hex = convert_to_hex(to_date)
    if(from_date_hex != "0" and to_date_hex!="0"):
        return 1

 
def validate_date(data):
    validation = 0
    # for i in range(7):
    #     print(int(data[i]))
    if int(data[1]) <= 12 and int(data[2]) <= 31 and int(data[4]) <= 24 and int(data[5]) <= 60 and int(data[6]) <= 60:
        print("Valid date and time.")
        validation = 1
    else:
        print("Invalid date and time.")
        validation =0

    return validation      

def convert_to_hex(number):
    # Split the number into parts separated by underscores
    status = "0"
    parts = number.split('-')
    res = validate_date(parts)
    if(res == 1):
    # Convert each part to hexadecimal with at least two characters
        hex_string = ''.join(format(int(part), '02x') for part in parts)
        status = "0"+hex_string
    else:   
        print("Please give valid date and time ")
        status = "0"
    return status



def ReadEventsprofilewithcount(serial_obj):

    VECount= readEventCount(serial_obj,"VECount","01C100070000636200FF0700")
    CECount= readEventCount(serial_obj,"CECount","01C100070000636201FF0700")
    PECount= readEventCount(serial_obj,"PECount","01C100070000636202FF0700")
    TECount= readEventCount(serial_obj,"TECount","01C100070000636203FF0700")
    OECount= readEventCount(serial_obj,"OECount","01C100070000636204FF0700")
    NECount= readEventCount(serial_obj,"NECount","01C100070000636205FF0700")
    print(VECount)
    print(CECount)
    print(PECount)
    print(TECount)
    print(OECount)
    print(NECount)

    VEpacket= readEventsProfile(serial_obj,"VE","01C100070000636200FF02",VECount)
    CEpacket= readEventsProfile(serial_obj,"CE","01C100070000636201FF02",CECount)
    PEpacket= readEventsProfile(serial_obj,"PE","01C100070000636202FF02",PECount)
    TEpacket= readEventsProfile(serial_obj,"TE","01C100070000636203FF02",TECount)
    OEpacket= readEventsProfile(serial_obj,"OE","01C100070000636204FF02",OECount)
    NEpacket= readEventsProfile(serial_obj,"NE","01C100070000636205FF02",NECount)
 
    data = VEpacket+CEpacket+PEpacket+TEpacket+OEpacket+NEpacket
    return data

def readOnDemand(serial_obj,profile):
    global fromentry,toentry,entry,finalstring
    eventspacket = "" 
    billing = "" 
    instapacket = "" 
    loadpacket = ""

    if(profile == "LOAD"):
        from_date = (sys.argv[2])
        to_date = (sys.argv[3])
        global from_date_hex,to_date_hex

        # Example number
        # number = "2024_04_24_11_"+metermake+"_00"

        # Convert to hexadecimal
        from_date_hex = convert_to_hex(from_date)
        to_date_hex = convert_to_hex(to_date)
        if(from_date_hex != "0" and to_date_hex!="0"):
            loadpacket = readLoadProfileReading(serial_obj)

    elif(profile == "INSTANT"): 
        instapacket = readInstantData(serial_obj)

    elif(profile == "BILLING"): 
        entry = (sys.argv[2])

        if(entry != "ALL"):
            entry = "1"
            fromentry = (sys.argv[2]) 
            toentry = (sys.argv[3])
        else:

            fromentry= ""
            toentry=""    
            billing = readBillingData(serial_obj)

    elif(profile == "EVENTS"):    
        eventspacket = ReadEventsprofilewithcount(serial_obj)   


    data = str(loadpacket)+str(instapacket)+str(billing)+str(eventspacket)

    data = gwid + ' ' + data
    print(data)

    # Encrypt the message
    # encrypted_data = encrypt_data(data, key)

    # jsonform = {
    #     "data": encrypted_data
    # }

    # # jsonform = "'EMReading':'"+str(split_strings[0])+"','WMReading':'"+str(split_strings[1])+"','Status':'"+str(relaystatus)+"'"
    # print(jsonform)
    # postdata(jsonform)

# ------------------------------- Code Begins here -------------------------------------------------------

def createkeys():

    hash_name = 'config_'+meterslno
    values = {

            'ipob' : '0',
            'isob' : '0',
            'ipsv' : '0',
            'lpob' : '0',
            'lsob' : '0',
            'lpsv' : '0',
            'bob' : '0',
            'bsv' : '0',
            'bsob' : '0',
            'eob' : '0',
            'esob' : '0',
            'esv' : '0',
            'rtc' : '0',
            'loadcapturetime' : '0',
            'configstatus' : '0'
    }

    # Set multiple values in the hash
    redis_client1.hset(hash_name, mapping=values)


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    print("ports")
    # usb_ports = [port.device for port in ports if 'ttyS' in port.description]
    usb_ports = [port.device for port in ports if 'COM' in port.description]
    print(usb_ports)
    return usb_ports

def getValue(data, delimiter, index):
    try:
        return data.split(delimiter)[index]
    except IndexError:
        return ""

def write_to_file(file_path, data):
    with open(file_path, "w") as f:
        f.write(str(data))
    f.close()

def append_to_file(file_path, data):
    with open(file_path, "a") as f:
        f.write(data)
    f.close()


def read_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read().strip()
    return "0"

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def readBillingOnDemand(serial_obj,commandid,commanddata):
    global fromentry,toentry,entry
    print(commanddata,type(commandid))
    try:
        if(commandid == "4"):
            print("read allll")
            billing = readBillingData(serial_obj)     

        elif(commandid == "10"):
            print("biill on demand")
            entry = "1"
            commanddata = commanddata.split("_")
            fromentry = (commanddata[0]) 
            toentry = (commanddata[1])
            billing = readBillingData(serial_obj)     
        return billing

    except Exception as e:
        print(e)
        return ""

def validate_date_load(data):
    validation = 0
    # for i in range(7):
    #     MSTLOG(int(data[i]))
    if int(data[1]) <= 12 and int(data[2]) <= 31 and int(data[4]) <= 24 and int(data[5]) <= 60 and int(data[6]) <= 60:
        MSTLOG("Valid date and time.")
        validation = 1
    else:
        MSTLOG("Invalid date and time.")
        validation =0

    return validation      


def datetohex(number):
    # Split the number into parts separated by underscores
    status = "0"
    parts = number.split('-')
    res = validate_date_load(parts)
    if(res == 1):
    # Convert each part to hexadecimal with at least two characters
        parts = parts[2]+"-"+parts[1]+"-"+parts[0]+"-"+parts[3]+"-"+parts[4]+"-"+parts[5]+"-"+parts[6]
        parts = parts.split('-')
        print(parts)
        hex_string = ''.join(format(int(part), '02x') for part in parts)
        status = "0"+hex_string
    else:   
        MSTLOG("Please give valid date and time ")
        status = "0"
    return status

   

def ReadOnDemandLoad(serial_obj,commandid,commanddata):
    global from_date_hex,to_date_hex
    try:
        loadpacket = ""
        fromdate = "" 
        to_date = ""
        print(commanddata,type(commandid))
        # try:
        if ((commandid) == "1"):
            fromdate = commanddata + "-00-00-00-00"
            to_date = commanddata + "-00-11-59-00"
            from_date_hex = datetohex(fromdate)
            to_date_hex = datetohex(to_date)

            if(from_date_hex != "0" and to_date_hex!="0"):
                print("VVV")
                loadpacket = readLoadProfileReading(serial_obj)

        elif ((commandid) == "11"):     
            loadpacket = readSclarObisValues(serial_obj,"L","01C100070100630100FF0200",)
        
        elif((commandid) == "15"):

            fromdate,to_date = commanddata.split("_")
            from_date_hex = convert_to_hex(fromdate)
            to_date_hex = convert_to_hex(to_date)
            if(from_date_hex != "0" and to_date_hex!="0"):
                loadpacket = readLoadProfileReading(serial_obj)

        return loadpacket

    except Exception as e:
        print(e)    
        return "0,0"

def CheckAndExecuteCommandsToNodes(command_to_node):
    try:
        print(command_to_node)
        print("command is " + command_to_node)

        commandtype = getValue(command_to_node, '|', 0)
        # print("commandtype: " + commandtype)

        meterno = getValue(command_to_node, '|', 1).strip()
        # print("IMEI: " + IMEI)

        CommandID = getValue(command_to_node, '|', 2)
        # print("CommandID: " + CommandID)

        CommandData = getValue(command_to_node, '|', 3)
        print("CommandData: " + CommandData)

        CommandIndex = getValue(command_to_node, '|', 4).strip()
        print("CommandIndex: " + CommandIndex)

        command_ack_string = "$" + nodeid + "_" + str(PhaseType) + "_" + "C_" + CommandIndex + "$"
        todayDate1 = "E:/home/lpu/KPTCL_rs485/logs1/"+meterslno+"_config_files.log"

        append_to_file(todayDate1,command_ack_string)
        append_to_file(todayDate,command_ack_string)  
        data = ""
        data = CommandID+":" + CommandData+","
        return data

    except Exception as e:
        print (e)


def ReadOnDemandCommandsStatus(serial_obj):
    data = read_file("E:/home/lpu/KPTCL_rs485/config"+meterslno+"_OnDemandCommands")
    try:
        if(len(data) > 2):
            commands = data.split(",")  # Split the string by commas
            for command in commands:
                commandtoberead = CheckAndExecuteCommandsToNodes(command.strip())  # Process each command individually

                print(commandtoberead)
                finaldata = ""
                print("commandtoberead",commandtoberead)
                if(len(commandtoberead) > 2):
                    commandtoberead = commandtoberead[0:len(commandtoberead)-1]
                    commands = commandtoberead.split(",")  # Split the string by commas
                    for command in commands:

                        CommandID = getValue(command, ':', 0)
                        print("CommandID: " + CommandID)

                        CommandData = getValue(command, ':', 1)
                        print("CommandData: " + CommandData)

                        if (((int(CommandID) == 1) or int(CommandID) == 11) or int(CommandID) == 15):  # Full Day Block Reading
                            print("lll")

                            finaldata = ReadOnDemandLoad(serial_obj,CommandID,CommandData)
                            
                        elif ((int(CommandID) == 4) or (int(CommandID) == 10)):  # Read Billing Profile

                            finaldata = readBillingOnDemand(serial_obj,CommandID,CommandData)

                        elif int(CommandID) == 5:  # Read Scalar

                            finaldata  = ReadScalar(serial_obj)

                        elif int(CommandID) == 6:  # Read events
                            finaldata = ReadEventsprofilewithcount(serial_obj)   

                        elif int(CommandID) == 7:  # Read OBIS
                            finaldata = ReadObis(serial_obj)

                        elif int(CommandID) == 9:  # Read Instantaneous

                            finaldata  = readAllProfiles(serial_obj,"IP","01C1000701005E5B00FF0200")                                   #InstantData

                        elif int(CommandID) == 13:  # Read Daily Load Profile

                            finaldata  = readAllProfiles(serial_obj,"DL","01C100070100630200FF0200") 
                        
                    
                    delete_file("E:/home/lpu/KPTCL_rs485/config"+meterslno+"_OnDemandCommands")


    except Exception as e:
        print (e)


def getData(url):
    status = ""
    try:
        # Headers with secretkey and authkey
        headers = {
            "secretkey": "tl2CxESUsQsQNNspCY4GHw"
        }

        # Send the GET request
        print(url)
        response = requests.get(url, headers=headers,timeout = 10)

        # Check the response
        if response.status_code == 200:
            data = response.text  # Assuming the response is JSON
            # print("Data:", data)
            status = data
        else:
            print("Failed to retrieve data. Status code:", response.status_code)
            print("Response:", response.text)

        return status

    except Exception as e:
        print(e)
        return 0    


# def gettime():
#     try:

#         url = "https://api.ms-tech.in/v11/gettime?gwid="
#         cfc = "0"
#         global_range = "22"
#         ciccid = "1234"
#         simeino = "1234567"
#         amemory = "14111111"
#         url = url + gwid + "&cv=" + str(gw_current_firmware_version)
#         write_to_file("E:/home/lpu/KPTCL_rs485/config/curr_ver.txt",str(gw_current_firmware_version))

#         data = getData(url)
#         print(data)

#     except Exception as e:
#         print(e)
#         return ""

def readMeterData(ports):
    print(ports)
    try:
        if ports:
            for port in ports:
                device_path = port
                print(device_path)
                # -------------------------- SERIAL INITIALIZATION -----------------------------------
                baud_rate = 9600  # Adjust this to the baud rate of your meter
                timeout = 10  # Timeout for reading from the serial port in seconds
                serial_obj = serial.Serial(device_path, baud_rate, timeout=timeout)
                # ======================================inputs=====================================
                profile = ""
                profile = "ALL"
                flagofautodetection = autodetection(serial_obj)
                if(flagofautodetection == 1):
                    readConfigurations(serial_obj,"METERNO","01C100010000600100FF0200")
                    print("meterslno",meterslno)  

                profilename = "0"

                if(len(meterslno) > 6):

                    resp = redis_client1.hget('config_'+meterslno , "configstatus")
                    resp = "None"
                    print(resp)

                    if(resp == {} or str(resp) == "None"):
                        configflag = 0
                        # createkeys()

                    else:
                        resp = resp.decode('utf-8')

                        if(int(resp) == 1):
                            print("lll")
                            configflag = int(resp)

                        elif(resp == 0):    
                            resp = redis_client1.hgetall('config_'+meterslno)
                            print(resp)
                            ipob = int(resp[b'ipob'].decode('utf-8'))
                            isob= int(resp[b'isob'].decode('utf-8'))
                            ipsv= int(resp[b'ipsv'].decode('utf-8'))
                            lsob= int(resp[b'lsob'].decode('utf-8'))
                            lpob= int(resp[b'lpob'].decode('utf-8'))
                            lpsv= int(resp[b'lpsv'].decode('utf-8'))
                            bob= int(resp[b'bob'].decode('utf-8'))
                            bsv= int(resp[b'bsv'].decode('utf-8'))
                            bsob= int(resp[b'bsob'].decode('utf-8'))
                            esv= int(resp[b'esv'].decode('utf-8'))
                            esob= int(resp[b'esob'].decode('utf-8'))
                            eob  = int(resp[b'eob'].decode('utf-8'))
                            rtc  = int(resp[b'rtc'].decode('utf-8'))

                            loadcapturetime  = int(resp[b'lct'].decode('utf-8'))

                    if(profile == "ALL"):
                        readAllProfiles(serial_obj)
                        ReadOnDemandCommandsStatus(serial_obj)


                    else:  
                        readOnDemand(serial_obj,profile)

                    
                print("-------------------------------------------------------------------------------------------------------"+"\n")
        else:
            print("No serial ports found.")


    except Exception as e:
        print(e)

meterslno = ""
ist_time = datetime.now(ist)

# todayDate = "E:/home/lpu/KPTCL_rs485_test/logs/"+str(ist_time.strftime('%Y-%m-%d_%H:%M:%S'))+".tmp"
# finalfilename  = "E:/home/lpu/KPTCL_rs485_test/logs/"+str(ist_time.strftime('%Y-%m-%d_%H:%M:%S'))+".log"


# def getcommands():
#     try:
#         meterslno = read_file("E:/home/lpu/KPTCL_rs485/config/meterslno_"+gwid)
#         url = "https://api.ms-tech.in/v11/getcommands?gwid="
#         url = url + meterslno
#         data = getData(url)
#         print(data)
#         if(len(data) > 5):
#             data = write_to_file("E:/home/lpu/KPTCL_rs485/config"+meterslno+"_OnDemandCommands",data)
#         return data
#     except Exception as e:
#         print(e)

def create_file(path):
    with open(path, "w") as file:
        pass  # Does nothing, just creates the file


def main():
    try:
        ports = list_serial_ports()
        
        # ports = ["/dev/ttyS2"] # Adjust this to your serial port
        ports = ["COM4"] # Adjust this to your serial port
        # create_file(todayDate)
        
        readMeterData(ports)
        # os.rename(todayDate,finalfilename)

    except Exception as e:
        print(e)        


if __name__ == "__main__":
    main()    
