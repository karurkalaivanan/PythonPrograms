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
# import redis
import pytz
import base64
import os
from pathlib import Path
ist = pytz.timezone('Asia/Kolkata')
import serial.tools.list_ports
import subprocess
ist_time = datetime.now(ist)


# version   1.1 
#==============================ENCRYPTION FUNCTIONS==============================

key = "tl2CxESUsQsQNNspCY4GHw"


#================================================================================
# os.popen("sudo -S chmod 777 /dev/ttyUSB0", 'w').write('123456789')

# ---------------------------REDIS---------------------------

# redis_client1 = redis.Redis(host='localhost', port=6379, db=2)

# --------------------------dir-------------
gwid = "NSKP900002"
nodeid = "NSKP900002"
debug = 1


# //////////////////////////////// Profile variables /////////////////////////////////////
gw_current_firmware_version = 1.1
# ////////////////////////////////////////////////////////////////////////////////////////////////////

def getPassword(meter):
    try:
        status = 1
        MSTLOG("Meter to be read is "+meter)
        meter.strip()
        meterindex = "00"
        if meter == "LT":
            llskey = "lnt1"
            meterindex = "00"
        
        elif meter == "AVON":
            llskey = "Hello"
            meterindex = "08"

        elif meter == "MAXWELL":
            llskey = "mx201199"
            meterindex = "01"


        elif meter == "LG":
            llskey = "11111111"
            meterindex = "02"


        elif meter == "SECURE":
            llskey = "ABCD0001"
            meterindex = "03"

        elif meter == "HPL":
            llskey = "1111111111111111"
            meterindex = "04"

        elif meter == "GENUS":
            llskey = "1A2B3C4D"
            meterindex = "05"

        elif meter == "CAP":
            llskey = "123456"
            meterindex = "06"

        elif meter == "EEPL":
            llskey = "ABCDEFGH"
            meterindex = "07"
            

        else:
            MSTLOG("unknown meter")
            llskey = "0"
            meterindex = "00"
            status = 0

        return status,llskey,meterindex

    except Exception as e:
        print(f"Error {e}")
        return status,llskey,meterindex


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

def get_sequence_number(nAct,g_RRR,g_SSS):
    # MSTLOG(g_RRR,g_SSS)
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
    return cFrameType,g_RRR,g_SSS


def bit_read(value, bit_position):
    return (value >> bit_position) & 1

def aarqframing(LLS_Keys):
    try:
        g_RRR = 0
        g_SSS = 0
        frame = ""
        startbit = "7E"
        aarqtag = "A0"
        #7E A0 0A 00 02 9C 1F 61 93 88 6D 7E
        serveraddress = "00029C1F"
        clientaddress = "41"
        ControlField,g_RRR,g_SSS = get_sequence_number(2,g_RRR,g_SSS)
        c,g_RRR,g_SSS = get_sequence_number(1,g_RRR,g_SSS);
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
        xDlmsRequest1 = "01000000065F1F040000181DFFFF" 
        lasttag = "7E"

        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(app_ctxt_name_1)+len(aARQ_aCSE_rEQs)+len(auth_mech_name_1)+len(password_tag)+len(password)+len(auth_password_or_public_Tag_len)+len(xDlmsRequest1)+8+4)/2)
        length = length1-11-6
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

        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+str(length)+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1

        datatocrc2 = bytes.fromhex(datatocrc2)
        crcoffull = crc(datatocrc2)

        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))


        crcoffull = str(lo)+str(hi)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+str(length)+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1+crcoffull+lasttag
        return frame,g_RRR,g_SSS
    
    except Exception as e:
        print(f"Error {e}")
        return frame,g_RRR,g_SSS
# -------------------------------------------------------------------------------------------


def instantframing():
    try:
        get_sequence_number(0);
        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "00029C1F"
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
        # MSTLOG(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # MSTLOG("crc1 " ,crcofhalf)
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
        print(f"Error {e}")

def commandframing(obis,g_RRR,g_SSS):
    try:
        c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS);
        frame = ""
        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "00029C1F"
        clientaddress = "41"
        ControlField,g_RRR,g_SSS = get_sequence_number(2,g_RRR,g_SSS)
        c,g_RRR,g_SSS = get_sequence_number(1,g_RRR,g_SSS);

        c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS);
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]

        hdlc = "E6E600"
        TAG_AARQ = "C0"
        xDlmsRequest1 = obis

        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+2+4+4)/2)
        # MSTLOG("len ;",(length1))
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
        return frame,g_RRR,g_SSS

    except Exception as e:
        print(f"Error {e}")
        return frame,g_RRR,g_SSS

def loadframing(fromdate,todate,g_RRR,g_SSS):
    try:
        c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS);
        frame = ""
        startbit = "7E"
        aarqtag = "A0"
        serveraddress = "00029C1F"
        clientaddress = "41"
        ControlField,g_RRR,g_SSS = get_sequence_number(2,g_RRR,g_SSS)
        c,g_RRR,g_SSS = get_sequence_number(1,g_RRR,g_SSS);

        c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS);
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]

        hdlc = "E6E600"
        TAG_AARQ = "C0"
        xDlmsRequest1 = "01C100070100630100FF02" 
        # 07E80412040B0000 07E80412040D0000
        # data = "01010204020412000809060000010000FF0F02120000090C"+from_year+from_month+from_date+from_day+from_hour+from_minute+from_second+"FF000000090C"+to_year+to_month+to_date+to_day+to_hour+to_minute+to_second+"FF0000000100"
        # crc 
        data = "01010204020412000809060000010000FF0F02120000090C"+fromdate+"FF000000090C"+todate+"FF0000000100"    
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+len(data)+2+4+4)/2)
        # MSTLOG("len ;",(length1))
        length1 = hex(length1)
        length1 = length1[2:]
        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # MSTLOG(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # MSTLOG("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # MSTLOG(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+data

        # MSTLOG(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # MSTLOG("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # MSTLOG(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # MSTLOG(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+data+crcoffull+lasttag
        # MSTLOG(frame)
        return frame,g_RRR,g_SSS

    except Exception as e:
        print(f"Error {e}")
        return frame,g_RRR,g_SSS


def supervisoryframing(g_RRR,g_SSS):
    try:
        frame = ""
        startbit = "7E"
        aarqtag = "A0"
        # length1 = 
        serveraddress = "00029C1F"
        clientaddress = "41"
        ControlField,g_RRR,g_SSS = get_sequence_number(3,g_RRR,g_SSS);
        # MSTLOG(ControlField)
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        # MSTLOG(str(ControlField))
        # ControlField = "323ABD"
        # get_sequence_number(1,g_RRR,g_SSS)
        # datatocrc =    
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+4+2)/2) #crc length 4 added 2 of length1
        # MSTLOG("len ;",(length1))
        # length1 = hex(length1)
        length1 = f"{length1:02X}"
        # MSTLOG("0x" + formatted_hex)
        # MSTLOG(length1)

        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # MSTLOG(dataforcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # MSTLOG("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # MSTLOG(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf

        # MSTLOG(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # MSTLOG("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # MSTLOG(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # MSTLOG(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+lasttag
        # MSTLOG(frame)
        return frame,g_RRR,g_SSS

    except Exception as e:
        print(f"Error {e}")
        return frame,g_RRR,g_SSS

def counterincrementer(iv1):
    # MSTLOG(iv1)
    try:
        integer_value = int(iv1, 16)
        new_integer_value = integer_value + 1

        invocation = hex(new_integer_value)[2:]
        invocation = invocation.zfill(len(iv1))
        # MSTLOG(invocation)
        return invocation

    except Exception as e:
        print(f"Error {e}")
        return "0"    


def specialframing(special_counter,g_RRR,g_SSS):
    try:
        frame = ""
        startbit = "7E"
        aarqtag = "A0"
        # length1 = 
        serveraddress = "00029C1F"
        clientaddress = "41"
        ControlField,g_RRR,g_SSS = get_sequence_number(2,g_RRR,g_SSS)
        c,g_RRR,g_SSS = get_sequence_number(1,g_RRR,g_SSS);
        # MSTLOG(ControlField)
        ControlField = hex((ControlField))
        ControlField = ControlField[2:]
        # MSTLOG(str(ControlField))
        # ControlField = "323ABD"
        # get_sequence_number(1,g_RRR,g_SSS)
        # datatocrc = 
        hdlc = "E6E600"
        # controlfield
        TAG_AARQ = "C0"
        # length
        dlms = "02C1"
        special_counter1 = special_counter
        MSTLOG(special_counter1)
        # special_counter = special_counter[2:]
        # #MSTLOG(special_counter)
        xDlmsRequest1 =  dlms + str(special_counter1)
        # crc 
        lasttag = "7E"
        length1 = int((len(aarqtag)+len(serveraddress)+len(clientaddress)+len(ControlField)+len(hdlc)+len(TAG_AARQ)+len(xDlmsRequest1)+2+4+4)/2)
        # MSTLOG("len ;",(length1))
        length1 = hex(length1)
        length1 = length1[2:]
        # /////////////////////// crc1 //////////////////////////

        dataforcrc1 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)
        # MSTLOG(datafo/rcrc1)
        dataforcrc1 = bytes.fromhex(dataforcrc1)
        crcofhalf = crc(dataforcrc1)
        # MSTLOG("crc1 " ,crcofhalf)
        hi, lo = crcofhalf >> 8, crcofhalf & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))
        crcofhalf =  str(lo)+str(hi)
        # MSTLOG(str(lo),str(hi)) 
        # ////////////////////////////////// crc 2 //////////////////////////////

        # datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+str(crcofhalf)+hdlc+TAG_AARQ+str(length)+clinetapplicationcontext+app_ctxt_name_1+aARQ_aCSE_rEQs+auth_mech_name_1+password_tag+password+auth_password_or_public_Tag_len+xDlmsRequest1


        datatocrc2 = aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1

        # MSTLOG(datatocrc2)
        datatocrc2 = bytes.fromhex(datatocrc2)


        crcoffull = crc(datatocrc2)
        # MSTLOG("crc2 " ,crcoffull)  
        hi, lo = crcoffull >> 8, crcoffull & 0xff

        hi=(format(hi, '02x'))
        lo=(format(lo, '02x'))

        # MSTLOG(str(lo),str(hi)) 

        crcoffull = str(lo)+str(hi)
        # MSTLOG(crcoffull)

        frame = startbit+aarqtag+str(length1)+serveraddress+clientaddress+str(ControlField)+crcofhalf+hdlc+TAG_AARQ+xDlmsRequest1+crcoffull+lasttag
        # MSTLOG(frame)
        return frame,g_RRR,g_SSS

    except Exception as e:
        print(f"Error {e}")

# def serial_write_read(serial_obj,con1):
#     try:
#         # con1 = con1 + b'\r\n'

#         for i in range(2):
#             res = 0
#             wait_count = 0
#             data_available = False
#             response_buffer = [] # Assuming you initialize your response buffer outside this function if needed
#             # print(con1)
#             # serial_obj.read(300)
#             # string_value = con1.hex()
#             # MSTLOG('ANOTHER REQUEST = ' + str(string_value)+"\n")


#             # command = 'echo 1 > /sys/class/gpio/P6_2/value'
#             # subprocess.run(command,shell=True,check=True)
            
#             # # con1 = bytearray.fromhex(commandforprofile)

#             # serial_obj.write(con1)
#             # serial_obj.flush()
#             # command = 'echo 0 > /sys/class/gpio/P6_2/value'
#             # subprocess.run(command,shell=True,check=True)
#             # # MSTLOG("hii")
#             # # time.sleep(0.5)
#             # if METER_DEBUG:
#             #     MSTLOG("RES: ", end='')
#             # while serial_obj.in_waiting >= 0:
#             #     if serial_obj.in_waiting > 0:
#             #         data_available = True
#             #         wait_count = 0
#             #         incoming_byte = serial_obj.read(1)

#             #         response_buffer.append(incoming_byte)

#             #         MSTLOG(incoming_byte.hex(), end=' ')
#             #         #     MSTLOG(incoming_byte)


#             #     else:
#             #         if wait_count > 5:
#             #             break
#             #         wait_count += 1
#             #         time.sleep(1)

#             #     # if(metertype == "LG"):
#             #     #     MSTLOG("lg")
                        

#             #     if data_available and serial_obj.in_waiting == 0:
#             #         # time.sleep(1)
#             #         if serial_obj.in_waiting == 0:
#             #             break


# # ===================================================================================================================
#             command = 'echo 1 | sudo tee /sys/class/gpio/P44_1/value'
#             subprocess.run(command, shell=True, check=True)
#             time.sleep(0.01)
#             # Ensure `con1` is correctly set before use
#             # con1 = bytearray.fromhex(commandforprofile)
#             serial_obj.write(con1)
#             serial_obj.flush()

#             command = 'echo 0 | sudo tee /sys/class/gpio/P44_1/value'
#             subprocess.run(command, shell=True, check=True)
#             # time.sleep(1)   

#             # if debug:
#                 # MSTLOG("RES: ")

#             response_buffer = []  # Assuming response_buffer is a list
#             wait_count = 0
#             data_available = False
#             count = 0
#             length = 0
#             while True:
#                 if serial_obj.in_waiting > 0:
#                     data_available = True
#                     wait_count = 0
#                     incoming_byte = serial_obj.read(1)
#                     count = count + 1
#                     response_buffer.append(incoming_byte)  # Ensure response_buffer is a list
#                     if(count == 3):
#                         hex_values = [f"{b[0]:02x}" for b in response_buffer] 
#                         length = getPacketLength(hex_values,count)
#                         # print(length)
#                     # MSTLOG(incoming_byte.hex()+str(, end=''))
#                 else:
#                     if (wait_count > 5 or ((count == length) and count != 0)):
#                         # print(count)
#                         # print(wait_count)
#                         break
#                     wait_count += 1
#                     time.sleep(0.5)

#                 # if data_available and serial_obj.in_waiting == 0:
#                 #     time.sleep(0.1)  # Slight delay to ensure all data is captured
#                 #     if(serial_obj.in_waiting == 0):
#                 #         break

# # ======================================================================================================================
#             # response = serial_obj.read(50)                                                           
#             # response_hex = response.hex()                                                   
#             # MSTLOG(f"Received Response: {response_hex}")                                        
     

#             # Set DATA_COMMUNICATION LOW
#             # digitalWrite(DATA_COMMUNICATION, LOW)

#             # incoming_bytes = serial_obj.read(300)
#             # serial_obj.flush()
#             #     # MSTLOG(incoming_bytes)
#             #     # output1 = str((incoming_bytes), 'UTF-8')
#             #     # MSTLOG(output1)
#             # if incoming_bytes:
#             #     response_buffer.extend(incoming_bytes)
#             # for b in response_buffer:  # Joins as one continuous hex string
#             #     MSTLOG(b)

#             # MSTLOG("\n")
#             # # exit(0)
#             # MSTLOG(response_buffer)
#             # serial_obj.flush()
#             # print("RES = ")
#             hex_string = "".join(f"{b[0]:02X}" for b in response_buffer)
#             MSTLOG(f"RES = {hex_string}")

#             res,output = responseparsing(response_buffer,"PACKETCHECK",0,"")
#             if(res == 1):
#                 break
#             else:
#                 time.sleep(1)   

#             # if(i == 4 and res !=1):
#             #     time.sleep(4)

#         return response_buffer,res

#     except Exception as e:
#         print(f"Error {e}") 
#         return response_buffer,res
   
def serial_write_read(serial_obj, con1):
    try:
        for i in range(2):
            res = 0
            wait_count = 0
            data_available = False
            response_buffer = []

            # command = 'echo 1 | sudo tee /sys/class/gpio/P44_1/value'
            # subprocess.run(command, shell=True, check=True)
            time.sleep(0.01)

            serial_obj.write(con1)
            serial_obj.flush()

            # command = 'echo 0 | sudo tee /sys/class/gpio/P44_1/value'
            # subprocess.run(command, shell=True, check=True)

            response_buffer = []
            wait_count = 0
            data_available = False
            count = 0
            length = 0

            while True:
                if serial_obj.in_waiting > 0:
                    data_available = True
                    wait_count = 0
                    incoming_byte = serial_obj.read(1)
                    count += 1
                    response_buffer.append(incoming_byte)

                    if count == 3:
                        hex_values = [f"{b[0]:02x}" for b in response_buffer]
                        length = getPacketLength(hex_values, count)

                else:
                    if (wait_count > 5 or ((count == length) and count != 0)):
                        break
                    wait_count += 1
                    time.sleep(0.5)

            # ============================ Extract frame from 0x7E to 0x7E ================================
            flat_bytes = [b[0] for b in response_buffer]

            try:
                start_index = flat_bytes.index(0x7E)
                end_index = len(flat_bytes) - 1 - flat_bytes[::-1].index(0x7E)

                if start_index < end_index:
                    frame_data = flat_bytes[start_index:end_index + 1]
                else:
                    frame_data = flat_bytes[start_index:]  # fallback

                response_buffer = [bytes([b]) for b in frame_data]

            except ValueError:
                MSTLOG("Start or end flag 0x7E not found in response")
                time.sleep(1)
                continue
            # ===========================================================================================

            hex_string = "".join(f"{b[0]:02X}" for b in response_buffer)
            MSTLOG(f"RES = {hex_string}")

            res, output = responseparsing(response_buffer, "PACKETCHECK", 0, "")
            if res == 1:
                break
            else:
                time.sleep(1)

        return response_buffer, res

    except Exception as e:
        print(f"Error {e}")
        return response_buffer, res

def readConfigurations(serial_obj,parameter,obis,LLS_Keys):
    try:
        for i in range (2):

            final_block = False
            frame_complete = False
            Block_response = False
            spaced_string = ""
            data = ""
            break_flag = 0
            try:

                MSTLOG("MR MODE METER "+parameter)

                # MSTLOG("MR MODE SNRM ")
                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    if(res == 1):
                        output = 0
                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                        
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0

                            res,data  = responseparsing(meterres,"AARQ",0,"") 
                            if(res == 1):
                                special_counter = "00000000"
                                commandforprofile,g_RRR,g_SSS = commandframing(obis,g_RRR,g_SSS)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('PHASE REQUEST = ' + str(commandforprofile)+"\n")
                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    res,data  = responseparsing(meterres,parameter,0,"") 
                                    # finalstring = finalstring + res + "_"
                                    if(res == 1):
                                        while (frame_complete):
                                            special_counter1 = counterincrementer(special_counter)  

                                            integer_value = int(hex_values[1], 16)
                                            check_a0 = bit_read((integer_value), 3)

                                            if(check_a0 == 0):
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter1,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                            
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                res,data = responseparsing(meterres,"SPECIALDATA",0,"") 
                                                integer_value = int(hex_values[1], 16)

                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                # MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                            else:
                                                MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break

                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 

            except Exception as e:
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"   

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        meterres,output = serial_write_read(serial_obj,con1)
        res = responseparsing(meterres,"SNRM",0,"") 
        g_RRR = 0
        g_SSS = 0
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        print(data)
        return data

    except Exception as e:
        print(f"Error {e}") 
        return "Null"

def readLoadProfileReading(serial_obj,LLS_Keys,metermake,meterslno,from_date_hex,to_date_hex,PhaseType):
    create_file(todayDate_load)

    try:
        for i in range (2):
            finalstring = ""
            final_block = False
            frame_complete = False
            Block_response = False
            spaced_string = ""
            special_counter = "00000000"
            status_func = 0
            final_string = ""
            output_profile = ""
            profilename = "L"
            break_flag = 0
            
            try:
                MSTLOG("MR MODE "+profilename)

                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    output = 0
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    MSTLOG(f"res {res}")
                    if(res == 1):

                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0
                            res,data = responseparsing(meterres,"AARQ",0,"") 

                            if(res == 1):
                                special_counter = "00000000"
                                commandforprofile,g_RRR,g_SSS = loadframing(from_date_hex,to_date_hex,g_RRR,g_SSS)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                                
                                
                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    status,hex_values,final_block,Block_response,frame_complete = responseParserForData(meterres) 
                                    final_string_data = hex_list_to_string(hex_values)
                                    final_string = final_string + final_string_data 
                                    # MSTLOG(f"final_string {(final_string)}")
                                    if(status == 1):

                                        while (frame_complete):
                                            integer_value = int(hex_values[1], 16)
                                            #MSTLOG(integer_value)
                                            check_a0 = bit_read((integer_value), 3)
                                            #MSTLOG(check_a0)

                                            if(check_a0 == 0):
                                                special_counter = counterincrementer(special_counter)  
                                                #MSTLOG(special_counter)
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                        
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                output = 0
                                                res,hex_values = responseparsing(meterres,"SPECIALDATA",0,"")
                                                final_string_data = hex_list_to_string(hex_values)
                                                final_string = final_string + final_string_data  
                                                # MSTLOG(res)
                                                integer_value = int(hex_values[1], 16)
                                                # Convert integer to binary string, remove '0b' prefix
                                                #binary_string = bin(integer_value)
                                                # #binary_string = bin(integer_value)
                                                #MSTLOG(type(binary_string))
                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                            
                                            else:
                                                MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break

                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")

            except Exception as e:
                MSTLOG(e)
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"                                # MSTLOG("MR MODE DISCONNECT ")

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        
        
        meterres,output = serial_write_read(serial_obj,con1)
        res,c = responseparsing(meterres,"SNRM",0,"")
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        if(break_flag == 1):
            final_string = ""
        output_profile = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+final_string[0:len(final_string)-1]+"$"  
        # MSTLOG(output_profile)
        append_to_file(todayDate_load,output_profile)
        append_to_file(todayDate,output_profile)  
        g_RRR = 0
        g_SSS = 0
        print(output_profile)

        return output_profile  

    except Exception as e:
        print(f"Error222 {e}") 
        return "Null"    

def readInstantData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):
    create_file(todayDate_ip)
    try:
        for i in range (2):

            finalstring = ""
            final_block = False
            frame_complete = False
            Block_response = False
            spaced_string = ""
            special_counter = "00000000"
            status_func = 0
            final_string = ""
            output_profile = ""
            profilename = "IP"
            break_flag = 0

            try:
                MSTLOG("MR MODE "+profilename)

                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    output = 0
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    MSTLOG(f"res {res}")
                    if(res == 1):

                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0
                            res,data = responseparsing(meterres,"AARQ",0,"") 

                            if(res == 1):
                                special_counter = "00000000"
                                commandforprofile,g_RRR,g_SSS = commandframing("01C1000701005E5B00FF0200",g_RRR,g_SSS)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                                
                                
                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    status,hex_values,final_block,Block_response,frame_complete = responseParserForData(meterres) 
                                    final_string_data = hex_list_to_string(hex_values)
                                    final_string = final_string + final_string_data 
                                    # MSTLOG(f"final_string {(final_string)}")
                                    if(status == 1):

                                        while (frame_complete):
                                            integer_value = int(hex_values[1], 16)
                                            #MSTLOG(integer_value)
                                            check_a0 = bit_read((integer_value), 3)
                                            #MSTLOG(check_a0)

                                            if(check_a0 == 0):
                                                special_counter = counterincrementer(special_counter)  
                                                #MSTLOG(special_counter)
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                        
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                output = 0
                                                res,hex_values = responseparsing(meterres,"SPECIALDATA",0,"")
                                                final_string_data = hex_list_to_string(hex_values)
                                                final_string = final_string + final_string_data  
                                                # MSTLOG(res)
                                                integer_value = int(hex_values[1], 16)
                                                # Convert integer to binary string, remove '0b' prefix
                                                #binary_string = bin(integer_value)
                                                # #binary_string = bin(integer_value)
                                                #MSTLOG(type(binary_string))
                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                                
                                            else:
                                                MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break
                
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")    

            except Exception as e:
                MSTLOG(e)
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"                                # MSTLOG("MR MODE DISCONNECT ")

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        
        
        meterres,output = serial_write_read(serial_obj,con1)
        res = responseparsing(meterres,"SNRM",0,"")
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        if(break_flag == 1):
            final_string = ""
        output_profile = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+final_string[0:len(final_string)-1]+"$"  
        # MSTLOG(output_profile)
        append_to_file(todayDate_ip,output_profile)
        append_to_file(todayDate,output_profile)  
        g_RRR = 0
        g_SSS = 0
        print(output_profile)

        return output_profile

    except Exception as e:
        print(f"Error {e}") 
        return "Null"    

def readSclarObisValues(serial_obj,profilename,obis,LLS_Keys,metermake,meterslno,PhaseType,file_flag):
    try:
        for i in range (2):

            finalstring = ""
            final_block = False
            frame_complete = False
            Block_response = False
            spaced_string = ""
            special_counter = "00000000"
            status_func = 0
            final_string = ""
            output_profile = ""
            break_flag = 0

            try:
                print("MR MODE "+profilename)

                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    output = 0
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    MSTLOG(f"res {res}")
                    if(res == 1):

                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0
                            res,data = responseparsing(meterres,"AARQ",0,"") 
                            print(data)
                            if(res == 1):
                                special_counter = "00000000"
                                commandforprofile,g_RRR,g_SSS = commandframing(obis,g_RRR,g_SSS)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                                
                                
                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    status,hex_values,final_block,Block_response,frame_complete = responseParserForData(meterres) 
                                    final_string_data = hex_list_to_string(hex_values)
                                    final_string = final_string + final_string_data 
                                    # MSTLOG(f"final_string {(final_string)}")
                                    if(status == 1):

                                        while (frame_complete):
                                            integer_value = int(hex_values[1], 16)
                                            # #MSTLOG(integer_value)
                                            check_a0 = bit_read((integer_value), 3)
                                            # #MSTLOG(check_a0)

                                            if(check_a0 == 0):
                                                special_counter = counterincrementer(special_counter)  
                                                # #MSTLOG(special_counter)
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                        
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                output = 0
                                                res,hex_values = responseparsing(meterres,"SPECIALDATA",0,"")
                                                final_string_data = hex_list_to_string(hex_values)
                                                final_string = final_string + final_string_data  
                                                # MSTLOG(final_string)
                                                integer_value = int(hex_values[1], 16)
                                                # Convert integer to binary string, remove '0b' prefix
                                                #binary_string = bin(integer_value)
                                                # #binary_string = bin(integer_value)
                                                #MSTLOG(type(binary_string))
                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                # MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                            else:
                                                # MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break

                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")

            except Exception as e:
                print(e)
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"                                # MSTLOG("MR MODE DISCONNECT ")

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        
        
        meterres,output = serial_write_read(serial_obj,con1)
        res = responseparsing(meterres,"SNRM",0,"")
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        if(break_flag == 1):
            final_string = ""
        output_profile = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+final_string[0:len(final_string)-1]+"$"  
        # MSTLOG(output_profile)
        
        if(file_flag == 1):
            append_to_file(os.path.join(base_dir, f"{meterslno}_config_files.log"),output_profile)
        elif(file_flag == 2):
            append_to_file(os.path.join(base_dir, f"{meterslno}_ONDemandload.log"),output_profile)
            
        append_to_file(todayDate,output_profile)  
        g_RRR = 0
        g_SSS = 0
        print(output_profile)
        return output_profile   

    except Exception as e:
        print(f"Error {e}") 
        return "Null"    


def readBillingData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType,entry,fromentry,toentry):
    try:
        for i in range (2):
            finalstring = ""
            final_block = False
            frame_complete = False
            Block_response = False
            spaced_string = ""
            special_counter = "00000000"
            status_func = 0
            final_string = ""
            output_profile = ""
            profilename = "B"
            break_flag = 0
            status = 1
            
            try:
                MSTLOG("MR MODE "+profilename)

                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    output = 0
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    MSTLOG(f"res {res}")
                    if(res == 1):

                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0
                            res,data = responseparsing(meterres,"AARQ",0,"") 
                            if(res == 1):
                                special_counter = "00000000"
                                # entry = "1"
                                # fromentry = "12"
                                # toentry = "13"
                                if(entry == 1):
                                    
                                    MSTLOG("in On_Demand")
                                    availableentry = format(int(fromentry), '02x')
                                    entriestoberead = format(int(toentry), '02x')
                                    # availableentry = "06"
                                    # entriestoberead = "07"
                                    ondemandframe = "0102020406000000"+availableentry+"06000000"+entriestoberead+"120001120000"
                                    commandforprofile,g_RRR,g_SSS = commandframing("01C100070100620100FF02"+ondemandframe,g_RRR,g_SSS)
                                else:
                                    MSTLOG("read all")
                                    commandforprofile,g_RRR,g_SSS = commandframing("01C100070100620100FF0200",g_RRR,g_SSS)
                                MSTLOG(commandforprofile)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('BILLING REQUEST = ' + str(commandforprofile)+"\n")
                                

                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    status,hex_values,final_block,Block_response,frame_complete = responseParserForData(meterres) 
                                    final_string_data = hex_list_to_string(hex_values)
                                    final_string = final_string + final_string_data 
                                    # MSTLOG(f"final_string {(final_string)}")
                                    if(status == 1):

                                        while (frame_complete):
                                            integer_value = int(hex_values[1], 16)
                                            #MSTLOG(integer_value)
                                            check_a0 = bit_read((integer_value), 3)
                                            #MSTLOG(check_a0)

                                            if(check_a0 == 0):
                                                special_counter = counterincrementer(special_counter)  
                                                #MSTLOG(special_counter)
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                        
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                output = 0
                                                res,hex_values = responseparsing(meterres,"SPECIALDATA",0,"")
                                                final_string_data = hex_list_to_string(hex_values)
                                                final_string = final_string + final_string_data  
                                                # MSTLOG(res)
                                                integer_value = int(hex_values[1], 16)
                                                # Convert integer to binary string, remove '0b' prefix
                                                #binary_string = bin(integer_value)
                                                # #binary_string = bin(integer_value)
                                                #MSTLOG(type(binary_string))
                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                            
                                            else:
                                                MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break

                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")

            except Exception as e:
                MSTLOG(e)
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                status = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"                                # MSTLOG("MR MODE DISCONNECT ")

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        
        
        meterres,output = serial_write_read(serial_obj,con1)
        res,c = responseparsing(meterres,"SNRM",0,"")
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        if(break_flag == 1):
            final_string = ""
            status = 0
        output_profile = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+final_string[0:len(final_string)-1]+"$"  
        # MSTLOG(output_profile)
        print(output_profile)
        append_to_file(os.path.join(base_dir, f"{meterslno}_billing.log"),output_profile)
        append_to_file(todayDate,output_profile)  
        g_RRR = 0
        g_SSS = 0        
        return output_profile,status  

    except Exception as e:
        print(f"Error {e}") 
        return "Null"    

def readEventsProfile(serial_obj,profilename,obis,LLS_Keys,metermake,meterslno,PhaseType,profilecount):
    try:
        for i in range (2):

            final_block = False
            frame_complete = False
            Block_response = False
            special_counter = "00000000"
            final_string = ""
            output_profile = ""
            break_flag = 0
            try:
                MSTLOG("MR MODE "+profilename)

                commandforprofile = "7EA00A00029C1F4193BB4E7E"
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                if(output == 1):
                    output = 0
                    res,data = responseparsing(meterres,"SNRM",0,"")
                    MSTLOG(f"res {res}")
                    if(res == 1):

                        commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                        con1 = bytearray.fromhex(commandforprofile)
                        MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                    
                        meterres,output = serial_write_read(serial_obj,con1)
                        if(output == 1):
                            output = 0
                            res,data = responseparsing(meterres,"AARQ",0,"") 

                            if(res == 1):
                                special_counter = "00000000"
                                if(profilecount > 5):
                                    profilecountfrom = format(int(profilecount-5), '02x')

                                else:
                                    profilecountfrom = "01"
                                profilecount = format((profilecount), '02x')
                    
                                eventspraming = "0102020406000000"+profilecountfrom+"06000000"+profilecount+"120001120000"
                                commandforprofile,g_RRR,g_SSS = commandframing(obis+eventspraming,g_RRR,g_SSS)
                                con1 = bytearray.fromhex(commandforprofile)
                                MSTLOG('INSTANT REQUEST = ' + str(commandforprofile)+"\n")
                                
                                
                                meterres,output = serial_write_read(serial_obj,con1)
                                if(output == 1):
                                    output = 0
                                    status,hex_values,final_block,Block_response,frame_complete = responseParserForData(meterres) 
                                    final_string_data = hex_list_to_string(hex_values)
                                    final_string = final_string + final_string_data 
                                    # MSTLOG(f"final_string {type(final_string)}")
                                    if(status == 1):

                                        while (frame_complete):
                                            integer_value = int(hex_values[1], 16)
                                            #MSTLOG(integer_value)
                                            check_a0 = bit_read((integer_value), 3)
                                            #MSTLOG(check_a0)

                                            if(check_a0 == 0):
                                                special_counter = counterincrementer(special_counter)  
                                                #MSTLOG(special_counter)
                                                commandforprofile,g_RRR,g_SSS = specialframing(special_counter,g_RRR,g_SSS)
                                            else:
                                                commandforprofile,g_RRR,g_SSS = supervisoryframing(g_RRR,g_SSS)  

                                            c,g_RRR,g_SSS = get_sequence_number(0,g_RRR,g_SSS)
                                            con1 = bytearray.fromhex(commandforprofile)
                                            MSTLOG('REQUEST = ' + str(commandforprofile)+"\n")
                                        
                                            meterres,output = serial_write_read(serial_obj,con1)
                                            if(output == 1):
                                                output = 0
                                                res,hex_values = responseparsing(meterres,"SPECIALDATA",0,"")
                                                final_string_data = hex_list_to_string(hex_values)
                                                final_string = final_string + final_string_data  
                                                # MSTLOG(res)
                                                integer_value = int(hex_values[1], 16)
                                                # Convert integer to binary string, remove '0b' prefix
                                                #binary_string = bin(integer_value)
                                                # #binary_string = bin(integer_value)
                                                #MSTLOG(type(binary_string))
                                                check_a0 = bit_read((integer_value), 3)

                                                if(Block_response == False):
                                                    if(check_a0 == 0):
                                                        frame_complete = False
                                                else:
                                                    if(Block_response == True and final_block == False):
                                                        # MSTLOG(f"hiii{len(hex_values)}")
                                                        if(len(hex_values) > 13):
                                                            if((hex_values[13+3] == "c1" or hex_values[13+3] == "81") and hex_values[14+3] == "01"):
                                                                MSTLOG("in")
                                                                if(check_a0 == 0):
                                                                    frame_complete = False
                                                                else:
                                                                    final_block = True    
                                                    else:
                                                        if(final_block == True):

                                                            if(check_a0 == 0):
                                                                frame_complete = False
                                                
                                            else:
                                                MSTLOG("out")
                                                break_flag = 1
                                                break
                                                break

                                        if(frame_complete == False or break_flag == 1):
                                            status_func = 1
                                            break
                    

                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                
                
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"")
    
            except Exception as e:
                MSTLOG(e)
                commandforprofile = "7EA00A00029C1F4153B7887E "
                con1 = bytearray.fromhex(commandforprofile)
                MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
                meterres,output = serial_write_read(serial_obj,con1)
                res = responseparsing(meterres,"SNRM",0,"") 
                g_RRR = 0
                g_SSS = 0
                MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")  
                return "Null"                                # MSTLOG("MR MODE DISCONNECT ")

        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")
        
        
        meterres,output = serial_write_read(serial_obj,con1)
        res = responseparsing(meterres,"SNRM",0,"")
        MSTLOG("----------------------------------------------------------------------------------------------------------------------------------")
        if(break_flag == 1):
            final_string = ""
        output_profile = "$"+nodeid+"_"+str(PhaseType)+"_"+profilename+"_06_"+metermake+"_"+meterslno+"_"+final_string[0:len(final_string)-1]+"$"  
        # MSTLOG(output_profile)
        # MSTLOG(output_profile)
        append_to_file(os.path.join(base_dir, f"{meterslno}_config_files.log"),output_profile)
        append_to_file(todayDate,output_profile)  
        g_RRR = 0
        g_SSS = 0
        print(output_profile)
        
        return output_profile

    except Exception as e:
        print(f"Error {e}") 
        return "Null"    

def responseParserForData(response):
    hex_values = []
    hex_values = [f"{b[0]:02x}" for b in response] 
    # hex_values = [f'{byte:02x}' for byte in response]  # As a list of hex strings
    status = 1    
    final_block = False
    frame_complete = False
    Block_response = False
    status = 0
    try: 
        if(len(hex_values)<10):
            return "0"

        if (hex_values[0] ==  "7e" or hex_values[2] != "00"):
            hex_list_to_string(hex_values)

            if (hex_values[11+3] ==  "c4"):   
                if (hex_values[12+3] ==  "02" ):
                    Block_response = True
                else:
                    if(hex_values[12+3] ==  "01" ):
                       Block_response = False 
            
            # MSTLOG(hex_values[1])
            integer_value = int(hex_values[1], 16)
            # Convert integer to binary string, remove '0b' prefix
            #binary_string = bin(integer_value)
            # #binary_string = bin(integer_value)
            #MSTLOG(type(binary_string))
            segment_action = bit_read((integer_value), 3)
            MSTLOG(f"this is a segment {segment_action}")
            status = 1
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

        # MSTLOG(f"{status} {hex_values} {final_block} {Block_response} {frame_complete}")
        return status,hex_values,final_block,Block_response,frame_complete

    except Exception as e:
        print(f"Error {e}") 
        return status,hex_values,final_block,Block_response,frame_complete


def getPacketLength(hex_values,length_from_packet):
    try:
        second_byte = int(hex_values[1], 16)  # a9 -> 169
        third_byte = int(hex_values[2], 16)   # 09 -> 9
        # Extract the last 3 bits from the 2nd byte
        second_byte_3bits = second_byte & 0b111  # Last 3 bits of a9 (169) -> 001 (binary)
        # Convert both to binary strings
        second_byte_3bits_bin = format(second_byte_3bits, '03b')  # Ensure 3-bit binary format
        third_byte_all_bits_bin = format(third_byte, '08b')  # Ensure 8-bit binary format
        # Append them (concatenate as a string)
        appended_binary = second_byte_3bits_bin + third_byte_all_bits_bin
        # Convert binary string to decimal
        decimal_result = int(appended_binary, 2)
        # print("Appended Binary:", appended_binary)
        # print("Decimal Value:", decimal_result)
        length = decimal_result + 2
        return length
    except Exception as e:
        return length_from_packet

def responseparsing(response,flag,iv1,profiletype):
    try:
        lct,availablebillentry = 0,0
        g_year = g_month = g_day = g_minutes = g_seconds = g_startingHour = 0    
        meterslno,countofeventsoccured ,PhaseType= "",0,0

        hex_values = [f"{b[0]:02x}" for b in response] 
        # hex_values = [f'{byte:02x}' for byte in response]  # As a list of hex strings
        status = 0
        data = ""
        length_packet = len(hex_values)
        # print(length_packet)
        length_byte = getPacketLength(hex_values,length_packet)
        # print(length_byte)

        # MSTLOG(type(hex_values[0]),flag)
        if(flag == "PACKETCHECK"):
            if((hex_values[length_packet-1] != "7e") or hex_values == [] or int(length_packet) != int(length_byte)):
                status = 0
                # print("erorrrrr")
            else:
                status =1    

        if(flag == "SNRM"):
            # if():
            status = 1
                # MSTLOG("snrm")


        elif(flag == "AARQ"):
            if(len(hex_values) > 20):
                if (hex_values[28] ==  "03" and hex_values[29] ==  "02" and
                    hex_values[30] ==  "01" and hex_values[31] ==  "00") and \
                   (hex_values[35] ==  "03" and hex_values[36] ==  "02" and
                    hex_values[37] ==  "01" and hex_values[38] ==  "00"):
                    MSTLOG("METER AARQ SUCCESS")
                    status = 1
                else:
                    MSTLOG("METER AARQ FAILURE")
                    status = 0
            

        elif(flag == "METERNO"):
            # Initialize variables
            if(len(hex_values)>15):

                ParsedMeterSerialNo = 0
                MeterSerialNo_Final = ""
                count = (int(hex_values[2],16))+ 2 - 3
                startColumnIndex = 18
                # Check if the value at ResponseBuffer[resIndex][startColumnIndex] is 0x06
                for resColumnIndex in range(startColumnIndex, count):
                    if hex_values[18] == "06" or hex_values[18] == "07":
                        # print("hii")
                        ParsedMeterSerialNo = (ParsedMeterSerialNo << 8) | int(hex_values[resColumnIndex+1],16)
                        MeterSerialNo_Final = MeterSerialNo_Final  + str(ParsedMeterSerialNo)
                        print(MeterSerialNo_Final)
                    elif hex_values[startColumnIndex] in ("09", "0a" , "0A") and resColumnIndex >= (startColumnIndex + 2):
                        MeterSerialNo_Final = MeterSerialNo_Final + str(hex_values[resColumnIndex])

                meterslno = bytes.fromhex(MeterSerialNo_Final).decode('utf-8')
                meterslno = meterslno.strip()
                MSTLOG(f"Meter Number is : {meterslno}")
                write_to_file(os.path.join(config_dir,f"meterslno_{gwid}"),meterslno)

                status = 1 
                data = meterslno                                   
            else:
                status = 0



        elif(flag == "EVENTCOUNT"):
            ProfileVEBytes = "0"
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15
            for resColumnIndex in range(startColumnIndex, count):
                if(flag == "EVENTCOUNT" and resColumnIndex >= (startColumnIndex + 1)):
                    ProfileVEBytes = ProfileVEBytes + str(hex_values[resColumnIndex]);
            
            countofeventsoccured = int((ProfileVEBytes),16)
            MSTLOG(f"ProfileVEBytes is : {countofeventsoccured}")
            data = countofeventsoccured
            status = 1

        elif(flag == "BILLENTRY"):
            ProfileVEBytes = "0"
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15+3
            for resColumnIndex in range(startColumnIndex, count):
                if(flag == "BILLENTRY" and resColumnIndex >= (startColumnIndex + 1)):
                    ProfileVEBytes = ProfileVEBytes + str(hex_values[resColumnIndex]);
            
            countofeventsoccured = int((ProfileVEBytes),16)
            MSTLOG(f"ProfileVEBytes is : {countofeventsoccured}")
            data = countofeventsoccured
            status = 1



        elif(flag == "SPECIALDATA"):
            # MSTLOG("special1") 
            # MSTLOG(hex_values[1])
            if(hex_values[0] == "7e" and hex_values[1] == "a0"):
                # MSTLOG("special")
                status = 1 
                # hex_values[13] = specialres[1]
                # hex_values[14] = specialres[2]
            data = hex_values

        elif(flag == "PHASE"):
            # MSTLOG("special1") 
            # MSTLOG(hex_values[1])
            if(hex_values[15] == "11"):
                startColumnIndex = 19
            else:
                startColumnIndex = 20
            
            MeterCategoryType = hex_values[startColumnIndex];
            
            if(MeterCategoryType == "5" or MeterCategoryType == "6"):
                PhaseType = 1
                status = 1

            else:
                PhaseType = 3
                status = 1

            
            MSTLOG(f"the phase type is {PhaseType}")
            data = PhaseType
           
        elif(flag == "RTC"):
            if (hex_values[0] ==  "7e" or hex_values[2] != "00"):
                # MSTLOG("special1") 
                # MSTLOG(hex_values[1])
                startRowIndex = 20;
                g_year = (int)(int(hex_values[startRowIndex],16) << 8 | int(hex_values[startRowIndex + 1],16));
                g_month = (int(hex_values[startRowIndex+2],16));
                g_day = (int(hex_values[startRowIndex+3],16));
                g_startingHour = int(hex_values[startRowIndex+5],16);
                g_minutes = int(hex_values[startRowIndex+6],16);
                g_seconds = int(hex_values[startRowIndex+7],16);
                if int(g_year) < 2000 and int(g_month) > 12 and int(g_day) > 31 and int(g_startingHour) > 24 and int(g_minutes) > 59 and int(g_seconds) > 59:
                    status = 0
                else:
                    MSTLOG("Meter RTC IS "+str(g_year)+" "+str(g_month)+" "+str(g_day)+" "+str(g_startingHour)+" "+str(g_minutes)+" "+str(g_seconds))
                    status = 1
                data = [g_year,g_month,g_day,g_startingHour,g_minutes,g_seconds]


        elif(flag == "LCT"):
                    # Initialize variables
            index = 0
            ddoublelongvalue= 0
            kWh_finalvalue = 0
            kWh_floatvalue = 0
            lct = ""
            count = (int(hex_values[2],16))+ 2 - 3
            startColumnIndex = 15+3
            # Check if the value at ResponseBuffer[resIndex][startColumnIndex] is 0x06
            for resColumnIndex in range(startColumnIndex, count):
                if hex_values[startColumnIndex] in ("09", "0A") and resColumnIndex >= (startColumnIndex + 2):
                    lct = str(lct)  + str(hex_values[resColumnIndex]) 
                    lct = int(lct,16)

                elif(hex_values[startColumnIndex] == "05" or hex_values[startColumnIndex] == "06"):
                    MSTLOG("hii")
                    while (startColumnIndex < (count-1)):

                        startColumnIndex = startColumnIndex+1
                        # MSTLOG(hex_values[startColumnIndex])
                        ddoublelongvalue = (ddoublelongvalue << 8) | int(hex_values[startColumnIndex],16)
                        # MSTLOG(ddoublelongvalue)
                    lct = str(ddoublelongvalue)
                elif (hex_values[startColumnIndex] == "12"):
                    while (startColumnIndex < (count-1)):
                        startColumnIndex = startColumnIndex+1

                        ddoublelongvalue = (ddoublelongvalue << 8) | int(hex_values[startColumnIndex],16);
                    lct = str(ddoublelongvalue)


            MSTLOG("The Load Captured Time is : "+str(lct))                       
            status = 1
            data = lct

        # MSTLOG(f"{status} {data} ")    
        return status,data        

    except Exception as e:
        print(f"Error {e}") 
        return status,data        

def ReadObis(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):
    try:
        data = ""
        ipobpacket = readSclarObisValues(serial_obj,"IPOB","01C1000701005E5B00FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #InstantdataObis 0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x03, 0x00
        isobpacket = readSclarObisValues(serial_obj,"ISOB","01C1000701005E5B03FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Instantobisscalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x03, 0x00
        lpobpacket = readSclarObisValues(serial_obj,"LPOB","01C100070100630100FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #LoaddataObis 0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x03, 0x00
        lsobpacket = readSclarObisValues(serial_obj,"LSOB","01C1000701005E5B04FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Loadobisscalar 0x07, 0x01, 0x00, 94, 91, 0x04, 0xFF, 0x03, 0x00
        bobpacket  = readSclarObisValues(serial_obj,"BOB", "01C100070100620100FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #BillingdataObis 0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x03, 0x00
        bsobpacket = readSclarObisValues(serial_obj,"BSOB","01C1000701005E5B06FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Billingobisscalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x03, 0x00
        eobpacket  = readSclarObisValues(serial_obj,"EOB", "01C100070000636201FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
        esobpacket = readSclarObisValues(serial_obj,"ESOB","01C1000701005E5B07FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
        dsobpacket = readSclarObisValues(serial_obj,"DSOB","01C1000701005E5B05FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
        dlobpacket = readSclarObisValues(serial_obj,"DLOB","01C100070100630200FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00

        data = ipobpacket+isobpacket+lpobpacket+lsobpacket+bsobpacket+bobpacket+esobpacket+eobpacket+dsobpacket+dlobpacket
        
        MSTLOG(data)    

        return data

    except Exception as e:
        MSTLOG(e)
        return "0,0"  

def ReadScalar(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):
    try:

        ipsvpacket = readSclarObisValues(serial_obj,"IPSV","01C1000701005E5B03FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #InstantScalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x02, 0x00
        lpsvpacket = readSclarObisValues(serial_obj,"LPSV","01C1000701005E5B04FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #LoadScalar 0x07, 0x01, 0x00, 94, 0x5B, 0x04, 0xFF, 0x02, 0x00
        bsvpacket  = readSclarObisValues(serial_obj,"BSV", "01C1000701005E5B06FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #BillingScalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x02
        esvpacket  = readSclarObisValues(serial_obj,"ESV", "01C1000701005E5B07FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
        dlsvpacket = readSclarObisValues(serial_obj,"DLSV","01C1000701005E5B05FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00

        data = ipsvpacket+lpsvpacket+bsvpacket+esvpacket+dlsvpacket
        
        MSTLOG(data)    

        return data

    except Exception as e:
        MSTLOG(e)
        return "Null"  


# ----------------------------------------------------AUTOMATION------------------------------------------------ 

def readProfilesForConfigurations(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):
    try:

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
        dsvpacket = "0"
        dsobpacket = "0"
        dobpacket = "0"

        print("inn")
    # ///////////////////////////////////////////////////ip configurations//////////////////////////////////////////////////////////////////////
            
        ipsvpacket= readSclarObisValues(serial_obj,"IPSV","01C1000701005E5B03FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #InstantScalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x02, 0x00
        
        ipobpacket= readSclarObisValues(serial_obj,"IPOB","01C1000701005E5B00FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #InstantdataObis 0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x03, 0x00
        
        isobpacket= readSclarObisValues(serial_obj,"ISOB","01C1000701005E5B03FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Instantobisscalar 0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x03, 0x00

    # # ///////////////////////////////////////////////////load configurations//////////////////////////////////////////////////////////////////////

            
        lpsvpacket= readSclarObisValues(serial_obj,"LPSV","01C1000701005E5B04FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #LoadScalar 0x07, 0x01, 0x00, 94, 0x5B, 0x04, 0xFF, 0x02, 0x00
    

        lpobpacket= readSclarObisValues(serial_obj,"LPOB","01C100070100630100FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #LoaddataObis 0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x03, 0x00
    

        lsobpacket= readSclarObisValues(serial_obj,"LSOB","01C1000701005E5B04FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Loadobisscalar 0x07, 0x01, 0x00, 94, 91, 0x04, 0xFF, 0x03, 0x00

    # # ////////////////////////////////////////////////////billing configurations/////////////////////////////////////////////////////////////////////


            
        bsvpacket= readSclarObisValues(serial_obj,"BSV","01C1000701005E5B06FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #BillingScalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x02

        
        bobpacket= readSclarObisValues(serial_obj,"BOB","01C100070100620100FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #BillingdataObis 0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x03, 0x00


        bsobpacket= readSclarObisValues(serial_obj,"BSOB","01C1000701005E5B06FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Billingobisscalar 0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x03, 0x00
        

    # # ////////////////////////////////////////////////////events configurations/////////////////////////////////////////////////////////////////////
    

        esvpacket= readSclarObisValues(serial_obj,"ESV","01C1000701005E5B07FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
    
    
        eobpacket= readSclarObisValues(serial_obj,"EOB","01C100070000636201FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
    
        
        esobpacket= readSclarObisValues(serial_obj,"ESOB","01C1000701005E5B07FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00

    # ////////////////////////////////////////////////////billing configurations/////////////////////////////////////////////////////////////////////


        dsvpacket= readSclarObisValues(serial_obj,"DLSV","01C1000701005E5B05FF0200",LLS_Keys,metermake,meterslno,PhaseType,1)   #EventScalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00
        
        dsobpacket= readSclarObisValues(serial_obj,"DSOB","01C1000701005E5B05FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00
        
        dobpacket= readSclarObisValues(serial_obj,"DLOB","01C100070100630200FF0300",LLS_Keys,metermake,meterslno,PhaseType,1)   #Eventobisscalar 0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00


    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
        
        data = ipsvpacket+ipobpacket+isobpacket+lpsvpacket+lpobpacket+lsobpacket+bsvpacket+bsobpacket+bobpacket+esvpacket+esobpacket+eobpacket+dsvpacket+dsobpacket+dobpacket
        
        MSTLOG(data)    

        return data

    except Exception as e:
        print(f"Error {e}") 

def ReadLoadProfile(serial_obj,LLS_Keys,metermake,rtc,lct,meterslno,PhaseType):
    try:
        l = "0"
        g_year, g_month, g_day, g_startingHour, g_minutes, g_seconds = rtc
        
        resp = read_file(os.path.join(config_dir,f"{meterslno}_fromdate"))
        # MSTLOG(resp)
        # if(resp.decode('utf-8')
        # resp = None
        day = "00"
        fromdate = ""
        todate =""
        datefrom = ""
        loadreadflag = 0
        MSTLOG(type(resp))
        if((resp) == None):
            
            ist_time = datetime.now(ist)
            datefrom = str(ist_time.strftime('%Y-%m-%d'))
            
            # fromdate = datefrom + "-"+day + "-00-00-00"
            fromdate = str(g_year)+"-"+str(g_month)+"-"+ str(g_day) + "-"+day + "-00-00-00"
            MSTLOG(fromdate)

        else:
            fromdate = resp 

    # -------------------------------------------------------------------------------------------------------------------
        
        split_strings = fromdate.split('-')

        fromdatefordiff = str(split_strings[0])+"-"+str(split_strings[1])+"-"+str(split_strings[2])+"-"+str(split_strings[4])+"-"+str(split_strings[5])+"-"+str(split_strings[6]) #2024-07-06
        todatefordiff = str(g_year)+"-"+str(g_month)+"-"+str(g_day)+"-"+str(g_startingHour)+"-"+str(g_minutes)+"-"+str(g_seconds)
        # MSTLOG(todatefordiff)
        # MSTLOG(fromdatefordiff)
    # -------------------------------------------------------------------------------------------------------------------
        date_format = "%Y-%m-%d-%H-%M-%S"

        diff1 = datetime.strptime(str(fromdatefordiff), date_format)
        diff2 = datetime.strptime(todatefordiff, date_format)

    # -------------------------------------------------------------------------------------------------------------------

        date_difference = diff2 - diff1
        total_seconds = date_difference.total_seconds()
        MSTLOG(total_seconds)
    # ---------------------------------------------------------------------------------------------------------------------
        if(total_seconds > 86400):
            ist_time = datetime.now(ist)
            datefrom = str(ist_time.strftime('%Y-%m-%d'))
            
            # fromdate = datefrom + "-"+day + "-00-00-00"
            fromdate = str(g_year)+"-"+str(g_month)+"-"+ str(g_day) + "-"+day + "-00-00-00"
            MSTLOG("fromdate"+str(fromdate))

    # ---------------------------------------------------------------------------------------------------------------------

        #     fromminte = str(split_strings[4])+"-"+str(split_strings[5])+"-"+str(split_strings[6]) 
        #     tominute = str(g_startingHour)+"-"+str(g_minutes)+"-"+str(g_seconds)
        #     MSTLOG(fromminte)
        #     MSTLOG(tominute)
        # # ---------------------------------------------------------------------------------------------------------------------

        #     datetime_format = "%H-%M-%S"

        #     fromtimediff1 = datetime.strptime(fromminte, datetime_format)
        #     totimediff2 = datetime.strptime(tominute, datetime_format)

        # # ---------------------------------------------------------------------------------------------------------------------
        #     # Calculate the difference
        #     datetime_difference = totimediff2 - fromtimediff1

        #     # Calculate the total difference in hours, minutes, and seconds
        #     total_seconds = datetime_difference.total_seconds()
        #     MSTLOG(total_seconds)
        # # -----------------------------------------------------------------------------------------------------------------------

        todate = str(g_year)+"-"+str(g_month)+"-"+str(g_day)+"-"+day+"-"+str(g_startingHour)+"-"+str(g_minutes)+"-"+str(g_seconds)
        loaddatetime = fromdate+","+todate
        print("From date is "+fromdate)
        print("To date is "+todate)
    # --------------------------------------------------------------------------------------------------------------------------

    # if(lct == 900 ):
        # MSTLOG(lct)
        if(total_seconds > int(lct)):
            

        # elif(lct == 1800):
        #     MSTLOG("in 1800")

        #     if(total_seconds > 1800):
        #         MSTLOG("in 30")
        #         loadreadflag = 1 

            split_strings = loaddatetime.split(',')
            status,from_date_hex,to_date_hex = checkdata(split_strings)

            if(status == 1):
                for i in range (2):
                    try:
                        l = readLoadProfileReading(serial_obj,LLS_Keys,metermake,meterslno,from_date_hex,to_date_hex,PhaseType) 
                        MSTLOG("load done")
                        # redis_client1.hset(meterslno+"_time","fromdate",todate)
                        write_to_file(os.path.join(config_dir, f"{meterslno}_fromdate"),todate)
                        break;
                    except Exception as e:
                        write_to_file(os.path.join(config_dir, f"{meterslno}_fromdate"),todate)
                        print(e)
                        
        else:
            MSTLOG("Load Profile Reading Time is Not Reached")

        return l

    except Exception as e:
        print(f"Error11111 {e}") 


def MSTLOG(resp):
    global debug
    if(debug == 1):
        print(resp)

def readBillingProfile(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):
    try:
        billingflag = 0
        b = "Null"
        ist_time = datetime.now(ist)
        presenttime = str(ist_time.strftime('%d')) 
        MSTLOG(presenttime)
        # time = None
        # time = redis_client1.hget(meterslno+"_billing","billingday")
        time = read_file(os.path.join(config_dir, f"{meterslno}_billing"))

        MSTLOG(time)
        # readoncebill = redis_client1.hget(meterslno+"_billing","readonceflag")
        readoncebill =  read_file(os.path.join(config_dir, f"{meterslno}_readonceflag_billing"))

        # readoncebill = None
        MSTLOG(readoncebill)
        if((time) == None):
            billingflag = 1
        else:
            MSTLOG(presenttime)
            # MSTLOG((time.decode('utf-8')))

            if((readoncebill) == None):
                readoncebill = "0"
                billingflag = 1
                MSTLOG(readoncebill)
            else:
                readoncebill = readoncebill
                    
        if(billingflag == 1):
            bill_entry = read_file(os.path.join(config_dir, f"{meterslno}_availablebillentry"))
            fromentry = int(bill_entry) - 1
            toentry = bill_entry
            b , status= readBillingData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType,1,fromentry,toentry)
            # b , status= readBillingData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType,0,0,0) #to read full billing

            if(status == 1):
                MSTLOG("billing")
                # redis_client1.hset(meterslno+"_billing","readonceflag",1)
                write_to_file(os.path.join(config_dir, f"{meterslno}_readonceflag_billing"),1)
                # redis_client1.hset(meterslno+"_billing","billingday",str(presenttime))
                write_to_file(os.path.join(config_dir, f"{meterslno}_billing"),str(presenttime))

                # write_to_file("/home/root/KPTCL_rs485/config/"+meterslno+"_billing",str(presenttime))

        return b

    except Exception as e:
        print(f"Error {e}") 

def autodetection(serial_obj):
    MSTLOG("AUTO DETECTION")
    autodetectionflag = 0
    metermake = ""
    LLS_Keys = ""  
    meters = [
        # "LT",
        "SECURE",
        # "AVON",
        # "MAXWELL",
        # "LG",
        # "HPL",
        # "GENUS",
        # "CAP",
        # "EEPL"
    ]


# ////   passwords ///////

    # passwordsofmeter = ["lnt1",
    #     "Hello",                #// lnt
    #    "mx201199", #// maxwell
    #    "11111111", #// LNG 
    #    "ABCD0001",     #// secure
    #    "1111111111111111",#// HPL
    #    "1A2B3C4D", #// GENUS
    #    "123456", #//CAP
    #    "ABCDEFGH"

    #    ] #// EEPL

    try: 
        for i in range (2):
            for i in range (len(meters)):
                try:
                    LLS_Keys = "" 

                    commandforprofile = "7EA00A00029C1F4193BB4E7E"
                    con1 = bytearray.fromhex(commandforprofile)
                    MSTLOG('SNRM REQUEST = ' + str(commandforprofile)+"\n")
                    meterres,output = serial_write_read(serial_obj,con1)
                    if(output == 1):
                        res,data = responseparsing(meterres,"SNRM",0,"")
                        if(res == 1):
                            MSTLOG(meters[i]) 
                            # LLS_Keys = passwordsofmeter[i] 
                            autodetectionflag,LLS_Keys,metermake = getPassword(meters[i])
 
                            commandforprofile,g_RRR,g_SSS = aarqframing(LLS_Keys)
                            # commandforprofile = "7EA04434110B3E1E6E606036802284A196760857458118A27808B76085745821AC68046C6E7431BE104E100065F1F4001E1DFFFF85157E"

                            con1 = bytearray.fromhex(commandforprofile)
                            MSTLOG('AARQ REQUEST = ' + str(commandforprofile)+"\n")
                            
                            meterres,output = serial_write_read(serial_obj,con1)
                            if(output == 1):

                                res,data = responseparsing(meterres,"AARQ",0,"") 
                                
                                if(res == 1):
                                    MSTLOG(meters[i])
                                    # autodetectionflag,LLS_Keys,metermake = getPassword(meters[i])
                                    break

                                else:
                                    commandforprofile = "7EA00A00029C1F4153B7887E "
                                    con1 = bytearray.fromhex(commandforprofile)
                                    MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")

                                    meterres,output = serial_write_read(serial_obj,con1)
                                    res,data = responseparsing(meterres,"SNRM",0,"") 
                                        

                except Exception as e:
                    MSTLOG("error",e)
                    return autodetectionflag,LLS_Keys,metermake


            if(autodetectionflag == 1):
                MSTLOG("d")
                break            

                
        commandforprofile = "7EA00A00029C1F4153B7887E "
        con1 = bytearray.fromhex(commandforprofile)
        MSTLOG('DISCONNECT REQUEST = ' + str(commandforprofile)+"\n")

        meterres,output = serial_write_read(serial_obj,con1)
        res,data = responseparsing(meterres,"SNRM",0,"")     
        MSTLOG("================================================================================================================================")
        return autodetectionflag,LLS_Keys,metermake

    except Exception as e:
        print(f"Error {e}") 
        return autodetectionflag,LLS_Keys,metermake

# def assignRedisVariables():
#     global g_startingHour
#     try:

#         presenttime = str(ist_time.strftime('%d')) 
#         time = redis_client1.hget(meterslno+"_billing","billingday")
#         # time = None
#         MSTLOG(type(time))

#         if((time) != None):
#             if((time).decode('utf-8') != str(presenttime) and g_startingHour == 1):
#                 redis_client1.hset(meterslno+"_billing","readonceflag",1)
#                 redis_client1.hset(meterslno+"_config","readonceflag",1)
#                 MSTLOG("hh")

#         readonceconfig = redis_client1.hget(meterslno+"_config","readonceflag")

#         # readonceconfig = None
#         if((readonceconfig) == None):
#            readonceconfig = "0"
#            MSTLOG("hii")
#         else:
#            readonceconfig = readonceconfig.decode('utf-8')
        
#         return readonceconfig

#     except Exception as e:
#         MSTLOG(e)

def assignRedisVariables(meterslno):

    rtc = read_file(os.path.join(config_dir, f"{meterslno}_rtc"))
    MSTLOG((rtc)) 
    g_year, g_month, g_day, g_startingHour, g_minutes, g_seconds = rtc.split(",")
    MSTLOG(g_startingHour)
    try: 

        presenttime = str(ist_time.strftime('%d')) 
        time = read_file(os.path.join(config_dir, f"{meterslno}_billing"))
        # time = None
        MSTLOG((time))

        if((time) != None):
            if((time) != str(presenttime) and int(g_startingHour) == 1):
                write_to_file(os.path.join(config_dir, f"{meterslno}_readonceflag",0))
                write_to_file(os.path.join(config_dir, f"{meterslno}_readonceflag_billing",0))
                write_to_file(os.path.join(config_dir, f"{meterslno}_config",0))
                MSTLOG("hh")

        readonceconfig = read_file(os.path.join(config_dir, f"{meterslno}_config"))

        # readonceconfig = None
        if((readonceconfig) == None):
           readonceconfig = "0"
           print("hii")
        else:
           readonceconfig = readonceconfig
        
        return readonceconfig

    except Exception as e:
        MSTLOG(e)
        return "0"


def readAllProfiles(serial_obj,LLS_Keys,metermake,meterslno):
    try:
        configfiles = "0"
        ippacket ="0"
        loadpacket = "0"
        events = "0"
        b = "0"
        dlpacket = "0"
        g_year = g_month = g_day = g_minutes = g_seconds = g_startingHour = 0    

        PhaseType = readConfigurations(serial_obj,"PHASE","01C1000100005E5B09FF0200",LLS_Keys)
        MSTLOG(datetime.now())
        print(os.path.join(config_dir, f"{meterslno}_PhaseType"))
        write_to_file(os.path.join(config_dir, f"{meterslno}_PhaseType"),PhaseType)

        rtc = readConfigurations(serial_obj,"RTC","01C100080000010000FF0200",LLS_Keys)   # char INST_Obiscode1[] = {0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0xFF, 0x02};
        print("rtc",rtc)
        write_to_file(os.path.join(config_dir, f"{meterslno}_rtc"),rtc)

        lct = readConfigurations(serial_obj,"LCT","01C100010100000804FF0200",LLS_Keys)   #EventdataObis 0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00
        write_to_file(os.path.join(config_dir, f"{meterslno}_lct"),(lct))

        availableentry = readConfigurations(serial_obj,"BILLENTRY","01C100070100620100FF0700",LLS_Keys)
        write_to_file(os.path.join(config_dir, f"{meterslno}_availablebillentry"),availableentry)

        readonceconfig = assignRedisVariables(meterslno)
        if(readonceconfig == "0"):
            
            configfiles = readProfilesForConfigurations(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)

            dlpacket = readSclarObisValues(serial_obj,"DL","01C100070100630200FF0200",LLS_Keys,metermake,meterslno,PhaseType,1) 

            events = ReadEventsprofilewithcount(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)   
            #                         #                                     #EventData
            write_to_file(os.path.join(config_dir, f"{meterslno}_config"),1)
        
        ippacket =  readInstantData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType) #InstantData       
        loadpacket = ReadLoadProfile(serial_obj,LLS_Keys,metermake,rtc,lct,meterslno,PhaseType)

        b = readBillingProfile(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)                                   #BillingData

    except Exception as e:
        MSTLOG(e)

# ---------------------------------------------------------------------------------------------------------------------------------------------

def hex_list_to_string(hex_list):
    # Join the hexadecimal values together
    finalstring = ""
    hex_string = ''.join(hex_list)
    spaced_string = ' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))
    finalstring = finalstring + spaced_string + "_"
    return finalstring


def checkdata(split_strings):
    from_date = (split_strings[0])
    to_date = (split_strings[1])

    # Convert to hexadecimal
    from_date_hex = convert_to_hex(from_date)
    to_date_hex = convert_to_hex(to_date)
    if(from_date_hex != "0" and to_date_hex!="0"):
        return 1,from_date_hex,to_date_hex

 
def validate_date(data):
    validation = 0
    # for i in range(7):
    #     MSTLOG(int(data[i]))
    if int(data[1]) <= 12 and int(data[2]) <= 31 and int(data[4]) <= 24 and int(data[5]) <= 59 and int(data[6]) <= 59:
        MSTLOG("Valid date and time.")
        validation = 1
    else:
        MSTLOG("Invalid date and time.")
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
        MSTLOG("Please give valid date and time ")
        status = "0"
    return status



def ReadEventsprofilewithcount(serial_obj,LLS_Keys,metermake,meterslno,PhaseType):

    VECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636200FF0700",LLS_Keys)
    CECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636201FF0700",LLS_Keys)
    PECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636202FF0700",LLS_Keys)
    TECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636203FF0700",LLS_Keys)
    OECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636204FF0700",LLS_Keys)
    NECount= readConfigurations(serial_obj,"EVENTCOUNT","01C100070000636205FF0700",LLS_Keys)
    MSTLOG(VECount)
    MSTLOG(CECount)
    MSTLOG(PECount)
    MSTLOG(TECount)
    MSTLOG(OECount)
    MSTLOG(NECount)

    VEpacket= readEventsProfile(serial_obj,"VE","01C100070000636200FF02",LLS_Keys,metermake,meterslno,PhaseType,VECount)
    CEpacket= readEventsProfile(serial_obj,"CE","01C100070000636201FF02",LLS_Keys,metermake,meterslno,PhaseType,CECount)
    PEpacket= readEventsProfile(serial_obj,"PE","01C100070000636202FF02",LLS_Keys,metermake,meterslno,PhaseType,PECount)
    TEpacket= readEventsProfile(serial_obj,"TE","01C100070000636203FF02",LLS_Keys,metermake,meterslno,PhaseType,TECount)
    OEpacket= readEventsProfile(serial_obj,"OE","01C100070000636204FF02",LLS_Keys,metermake,meterslno,PhaseType,OECount)
    NEpacket= readEventsProfile(serial_obj,"NE","01C100070000636205FF02",LLS_Keys,metermake,meterslno,PhaseType,NECount)
 
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
    MSTLOG(data)

    # Encrypt the message
    # encrypted_data = encrypt_data(data, key)

    # jsonform = {
    #     "data": encrypted_data
    # }

    # # jsonform = "'EMReading':'"+str(split_strings[0])+"','WMReading':'"+str(split_strings[1])+"','Status':'"+str(relaystatus)+"'"
    # MSTLOG(jsonform)
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
    # redis_client1.hset(hash_name, mapping=values)


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    MSTLOG("ports")
    usb_ports = [port.device for port in ports if 'USB' in port.description]
    MSTLOG(usb_ports)
    return usb_ports

def getValue(data, delimiter, index):
    try:
        return data.split(delimiter)[index]
    except IndexError:
        return ""

import os

def write_to_file(file_path, data):
    """Writes data to a file. Creates the file if it doesn't exist."""
    print(file_path)
    try:
        with open(file_path, "w") as f:
            f.write(str(data))
        print(f" Data successfully written to {file_path}")
    except Exception as e:
        print(f" Error writing to file {file_path}: {e}")

def append_to_file(file_path, data):
    """Appends data to a file. Creates the file if it doesn't exist."""
    try:
        with open(file_path, "a") as f:
            f.write(str(data))
        print(f" Data successfully appended to {file_path}")
    except Exception as e:
        print(f" Error appending to file {file_path}: {e}")

def read_file(file_path):
    """Reads content from a file if it exists."""
    print(file_path)
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read().strip()
        else:
            print(f"Warning: File '{file_path}' does not exist.")
            return None
    except Exception as e:
        print(f" Error reading file {file_path}: {e}")
        return None

def delete_file(file_path):
    """Deletes a file if it exists, otherwise raises a warning."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f" File '{file_path}' deleted successfully.")
        else:
            print(f"Warning: Cannot delete '{file_path}', file does not exist.")
    except Exception as e:
        print(f" Error deleting file {file_path}: {e}")

def readBillingOnDemand(serial_obj,commandid,commanddata,LLS_Keys,metermake,meterslno,PhaseType):
    MSTLOG(commanddata)
    try:
        if(commandid == "4"):
            MSTLOG("read allll")
            billing = readBillingData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType,0,0,0)     

        elif(commandid == "10"):
            MSTLOG("biill on demand")
            entry = "1"
            commanddata = commanddata.split("_")
            fromentry = (commanddata[0]) 
            toentry = (commanddata[1])
            billing = readBillingData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType,entry,fromentry,toentry)     
        return billing

    except Exception as e:
        MSTLOG(e)
        return ""

def validate_date_load(data):
    validation = 0
    # for i in range(7):
    #     MSTLOG(int(data[i]))
    if int(data[0]) <= 31 and int(data[1]) <= 12 and int(data[4]) <= 24 and int(data[5]) <= 60 and int(data[6]) <= 60:
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
        MSTLOG(parts)
        hex_string = ''.join(format(int(part), '02x') for part in parts)
        status = "0"+hex_string
    else:   
        MSTLOG("Please give valid date and time ")
        status = "0"
    return status

   

def ReadOnDemandLoad(serial_obj,commandid,commanddata,LLS_Keys,metermake,meterslno,PhaseType):
    try:
        loadpacket = ""
        fromdate = "" 
        to_date = ""
        MSTLOG(f"commanddata {type(commandid)}")
        # try:
        if ((commandid) == "1"):
            fromdate = commanddata + "-00-00-00-00"
            to_date = commanddata + "-00-11-59-00"
            from_date_hex = datetohex(fromdate)
            to_date_hex = datetohex(to_date)

            if(from_date_hex != "0" and to_date_hex!="0"):
                MSTLOG("VVV")
                loadpacket = readLoadProfileReading(serial_obj,LLS_Keys,metermake,meterslno,from_date_hex,to_date_hex,PhaseType) 

        elif ((commandid) == "11"):     
            loadpacket = readSclarObisValues(serial_obj,"L","01C100070100630100FF0200",LLS_Keys,metermake,meterslno,PhaseType,2)
        
        elif((commandid) == "15"):

            fromdate,to_date = commanddata.split("_")
            from_date_hex = convert_to_hex(fromdate)
            to_date_hex = convert_to_hex(to_date)
            if(from_date_hex != "0" and to_date_hex!="0"):
                loadpacket = readLoadProfileReading(serial_obj,LLS_Keys,metermake,meterslno,from_date_hex,to_date_hex,PhaseType) 

        return loadpacket

    except Exception as e:
        print(e)    
        return "0,0"

def CheckAndExecuteCommandsToNodes(command_to_node,meterslno,PhaseType):
    try:
        MSTLOG(command_to_node)
        MSTLOG("command is " + command_to_node)
        data = "0"
        commandtype = getValue(command_to_node, '|', 0)
        # MSTLOG("commandtype: " + commandtype)

        meterno = getValue(command_to_node, '|', 1).strip()
        MSTLOG("meterno: " + meterno.strip() + str(meterslno).strip())

        if meterno.strip() == str(meterslno).strip():
            CommandID = getValue(command_to_node, '|', 2)
            MSTLOG("CommandID: " + CommandID)

            CommandData = getValue(command_to_node, '|', 3)
            MSTLOG("CommandData: " + CommandData)

            CommandIndex = getValue(command_to_node, '|', 4).strip()
            MSTLOG("CommandIndex1: " + CommandIndex)

            command_ack_string = "$" + nodeid + "_" + str(PhaseType) + "_" + "C_" + CommandIndex + "$"

            append_to_file(os.path.join(base_dir, f"{meterslno}_config_files.log"),command_ack_string)
            append_to_file(todayDate,command_ack_string)  
            
            data = CommandID+":" + CommandData+","
        return data

    except Exception as e:
        MSTLOG(e)

def delete_commands(path,data_toberemoved):
    MSTLOG("DELETE")
    MSTLOG(path)
    MSTLOG(data_toberemoved)

    try:
        with open(path, "r") as file:
            content = file.read()
            print("content",content)
            
        # Remove "a" only and clean up extra commas
        content1 = content.replace(data_toberemoved+",", "").replace(","+data_toberemoved, "").replace(data_toberemoved, "")
        print("content1",content1)

        with open(path, "w") as file:
            file.write(content1)
            
    except Exception as e:
        MSTLOG(e)        

def ReadOnDemandCommandsStatus(serial_obj,LLS_Keys,metermake,meterslno):
    
    PhaseType = read_file(os.path.join(config_dir,f"{meterslno}_PhaseType"))
    filename = os.path.join(config_dir,f"{meterslno}_OnDemandCommands")
    data = read_file(filename)
    MSTLOG(data)
    try:
        if((data) != None):
            if(len(data) > 5 ):
                commands = data.split(",")  # Split the string by commas
                MSTLOG(commands)
                for command in commands:
                    MSTLOG(command)
                    commandtoberead = CheckAndExecuteCommandsToNodes(command.strip(),meterslno,PhaseType)  # Process each command individually

                    MSTLOG(commandtoberead)
                    MSTLOG(f"commandtoberead {commandtoberead}")
                    if(len(commandtoberead) > 2):
                        commandtoberead = commandtoberead[0:len(commandtoberead)-1]
                        commands_sub = commandtoberead.split(",")  # Split the string by commas
                        for command_toread in commands_sub:

                            CommandID = getValue(command_toread, ':', 0)
                            MSTLOG("CommandID: " + CommandID)

                            CommandData = getValue(command_toread, ':', 1)
                            MSTLOG("CommandData: " + CommandData)

                            if (((int(CommandID) == 1) or int(CommandID) == 11) or int(CommandID) == 15):  # Full Day Block Reading
                                MSTLOG("lll")

                                finaldata = ReadOnDemandLoad(serial_obj,CommandID,CommandData,LLS_Keys,metermake,meterslno,PhaseType)
                                
                            elif ((int(CommandID) == 4) or (int(CommandID) == 10)):  # Read Billing Profile

                                finaldata = readBillingOnDemand(serial_obj,CommandID,CommandData,LLS_Keys,metermake,meterslno,PhaseType)

                            elif int(CommandID) == 5:  # Read Scalar

                                finaldata  = ReadScalar(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)

                            elif int(CommandID) == 6:  # Read events
                                finaldata = ReadEventsprofilewithcount(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)   

                            elif int(CommandID) == 7:  # Read OBIS
                                finaldata = ReadObis(serial_obj,LLS_Keys,metermake,meterslno,PhaseType)

                            elif int(CommandID) == 9:  # Read Instantaneous

                                finaldata =  readInstantData(serial_obj,LLS_Keys,metermake,meterslno,PhaseType) #InstantData       

                            elif int(CommandID) == 13:  # Read Daily Load Profile

                                finaldata = readSclarObisValues(serial_obj,"DL","01C100070100630200FF0200",LLS_Keys,metermake,meterslno,PhaseType,1) 
                            
                        
                        delete_commands(filename,command)


    except Exception as e:
        MSTLOG(e)


def getData(url):
    status = ""
    try:
        # Headers with secretkey and authkey
        headers = {
            "secretkey": "tl2CxESUsQsQNNspCY4GHw"
        }

        # Send the GET request
        MSTLOG(url)
        response = requests.get(url, headers=headers,timeout = 10)

        # Check the response
        if response.status_code == 200:
            data = response.text  # Assuming the response is JSON
            # MSTLOG("Data:", data)
            status = data
        else:
            MSTLOG(f"Failed to retrieve data. Status code: {response.status_code}")
            MSTLOG(f"Response: { response.text}")

        return status

    except Exception as e:
        MSTLOG(e)
        return 0    


def gettime():
    try:

        url = "https://api.ms-tech.in/v11/gettime?gwid="
        cfc = "0"
        global_range = "22"
        ciccid = "1234"
        simeino = "1234567"
        amemory = "14111111"
        url = url + gwid + "&cv=" + str(gw_current_firmware_version)

        write_to_file(os.path.join(config_dir, f"curr_ver.txt"),str(gw_current_firmware_version))
        data = getData(url)
        print(data)
        write_to_file(os.path.join(config_dir, f"timeresponse.txt"),gwid+data)    

    except Exception as e:
        print("error",e)
        return ""

def readMeterData(ports):
    try:
        if ports:
            for port in ports:
                device_path = port
                MSTLOG(device_path)
                # os.system(f'sudo chmod 777 {device_path}')

                # -------------------------- SERIAL INITIALIZATION -----------------------------------
                baud_rate = 9600  # Adjust this to the baud rate of your meter
                timeout = 1  # Timeout for reading from the serial port in seconds
                serial_obj = serial.Serial(device_path, baud_rate, timeout=timeout)

                # ======================================inputs=====================================

                profile = ""
                profile = "ALL"
                MSTLOG("START TIME - "+str(ist_time.strftime('%Y-%m-%d %H:%M:%S'))+"\n")

                flagofautodetection,LLS_Keys,metermake = autodetection(serial_obj)
                # LLS_Keys = "ABCD0001"
                # metermake = "03"
                # flagofautodetection = 1
                if(flagofautodetection == 1):
                    for i in range(5):
                        meterslno = readConfigurations(serial_obj,"METERNO","01C100010000600100FF0200",LLS_Keys)
                        if(len(meterslno) > 6):
                            break
                    print(f"meterslno {meterslno}")  

                profilename = "0"

                if(len(meterslno) > 6):

                    # resp = redis_client1.hget('config_'+meterslno , "configstatus")
                    resp = "None"
                    MSTLOG(resp)

                    if(resp == {} or str(resp) == "None"):
                        configflag = 0
                        # createkeys()

                    else:
                        resp = resp.decode('utf-8')

                        if(int(resp) == 1):
                            MSTLOG("lll")
                            configflag = int(resp)

                        elif(resp == 0):    
                            # resp = redis_client1.hgetall('config_'+meterslno)
                            MSTLOG(resp)
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
                        readAllProfiles(serial_obj,LLS_Keys,metermake,meterslno)
                        ReadOnDemandCommandsStatus(serial_obj,LLS_Keys,metermake,meterslno)


                    else:  
                        readOnDemand(serial_obj,profile)

                    
                MSTLOG("-------------------------------------------------------------------------------------------------------"+"\n")
        else:
            MSTLOG("No serial ports found.")


    except Exception as e:
        MSTLOG(e)

def getcommands():
    try:
        meterslno = read_file(os.path.join(config_dir,f"meterslno_{gwid}"))
        url = "https://api.ms-tech.in/v11/getcommands?gwid="
        url = url + meterslno
        data = getData(url)
        MSTLOG(meterslno)
        MSTLOG(data)
        data = "N|NSTG702908|4|1|JRfpPF9f,N|Q0246104|5|1|JRfpPF9f"
        if(len(data) > 5):
            write_to_file (os.path.join(config_dir, f"{meterslno}_OnDemandCommands"),data)
        return data
    except Exception as e:
        MSTLOG(e)

def create_file(path):
    try:
        if not os.path.exists(path):
            with open(path, 'w') as file:
                pass  # Create an empty file

    except Exception as e:
        print(e)
        
def create_file_write(path,data):
    try:
        with open(path, "w") as f:
            f.write(str(data))   

    except Exception as e:
        print(e)

def create_dir(dir_name):
    print(dir_name)
    try:
        os.makedirs(dir_name, exist_ok=False)  # Raises an error if the directory exists
        print("Directory created successfully.")
    except FileExistsError:
        print(f"Error: The directory '{dir_name}' already exists.")
      

def get_username():
    path = (os.path.expanduser("~"))  # Gets home directory
    return path
def update_file(old_name,new_name):
    try:
        if os.path.exists(old_name):
            os.rename(old_name,new_name)
    except Exception as e:
        print(e)

def internetDataSender():
    gettime()
    getdata = getcommands()
    return getdata

def file_setup():
    try:
        # Define base directories

        # Create directories
        for directory in [base_dir_test, base_dir, config_dir]:
            create_dir(directory)

        # Create and write to files
        gwid_file = os.path.join(config_dir, "gwid.txt")
        ver_file = os.path.join(config_dir, "curr_ver.txt")
        create_file_write(gwid_file, gwid)
        create_file_write(ver_file, gw_current_firmware_version)

        # Get timestamp
        ist_time = datetime.now().strftime('%Y-%m-%d-%H:%M:%S')
        print("Files and directories created successfully.")

    except Exception as e:
        print(f"Error: {e}")

meterslno = ""
path = get_username()
base_dir_test = path+"/test_Genus/KPTCL_rs485_test/logs"
base_dir = path+"/test_Genus/KPTCL_rs485/logs"
config_dir = path+"/test_Genus/KPTCL_rs485/config"
ist_time = datetime.now(ist)

# creating files for load and instant
file_setup()
todayDate = os.path.join(base_dir_test, f"{ist_time}.tmp")
finalfilename = os.path.join(base_dir_test, f"{ist_time}.log")

todayDate_ip = os.path.join(base_dir, f"IP_{ist_time}.tmp")
finalfilename_ip = os.path.join(base_dir, f"IP_{ist_time}.log")

todayDate_load = os.path.join(base_dir, f"L_{ist_time}.tmp")
finalfilename_load = os.path.join(base_dir, f"L_{ist_time}.log")

# todayDate_config = os.path.join(base_dir, f"{meterslno}_config_files.tmp")
# finalfilename_config = os.path.join(base_dir, f"{meterslno}_config_files.log")

# todayDate_bill = os.path.join(base_dir, f"{meterslno}_billing.tmp")
# finalfilename_bill = os.path.join(base_dir, f"{meterslno}_billing.log")


def main():
    try:
        print("neww")
        ports = list_serial_ports()  

        # os.system(f'sudo chmod 777 /dev/ttyUSBS0')
        ports = ["COM8"] # Adjust this to your serial port
        create_file(todayDate)
        # data = internetDataSender()
        readMeterData(ports)

        update_file(todayDate,finalfilename)
        update_file(todayDate_ip,finalfilename_ip)
        update_file(todayDate_load,finalfilename_load)

    except Exception as e:
        print(e)        


if __name__ == "__main__":
    main()    
