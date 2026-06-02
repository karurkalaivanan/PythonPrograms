import serial
import time
from enum import Enum

#Global Variables
response_buffer = []
data_value = 0
meter_phase = 0

g_RRR = 0
g_SSS = 0
ObiscodeIndex = 0
unciperIframe = bytearray(128)
Hdlc_OutBuf = bytearray(255)
MAX_SIZE = 255
LoadREQframeptr = bytearray(MAX_SIZE)

# ENUM DECLARATION
DATA = 1
VALUE = 2
OBIS = 3
PROFILE = 7
CLOCK = 8

def hdlc_ChksumCalculate(fcs, pcp, length):
    fcstab = [
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
        0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
        0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
        0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
        0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
        0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
        0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
        0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
        0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
        0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
        0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
        0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
        0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
        0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
        0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
        0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
        0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
        0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
        0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
        0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
        0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
        0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
        0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
        0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
        0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
        0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
        0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
        0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
        0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78]

    for i in range(length):
        fcs = ((fcs >> 8) ^ fcstab[(fcs ^ pcp[i]) & 0xff])

    return fcs

class Frametypes(Enum):
    INFORMATION_FRAME = 1
    SUPERVISORY_FRAME = 2
    SNRM_FRAME = 3
    DISCONNECT_FRAME = 4
    SPECIAL_FRAME = 100  
class Metercommands(Enum):
    CMD_SNRM = 1
    CMD_AARQ = 2
    CMD_METER_SNO = 3
    CMD_METER_TYPE = 4
    CMD_METER_RTC = 5
    CMD_INSTANT_PARAM = 6
    CMD_BILLING_PARAM = 7
    CMD_LP_DATA = 8
    CMD_METER_DISC = 9
class DLMS_DATA_TYPE(Enum):
    NONE = 0
    BOOLEAN = 3
    BIT_STRING = 4
    INT32 = 5
    UINT32 = 6
    OCTET_STRING = 9
    STRING = 10
    BINARY_CODED_DESIMAL = 13
    STRING_UTF8 = 12
    INT8 = 15
    INT16 = 16
    UINT8 = 17
    UINT16 = 18
    INT64 = 20
    UINT64 = 21
    ENUM = 22
    FLOAT32 = 23
    FLOAT64 = 24
    DATETIME = 25
    DATE = 26
    TIME = 27
    ARRAY = 1
    STRUCTURE = 2
    COMPACT_ARRAY = 19
    BYREF = 0x80
        
cmd_Snrm = [0x7E, 0xA0, 0x07, 0x03, 0x41, 0x93, 0x5A, 0x64, 0x7E]
cmd_Aarq = [0x7E, 0xA0, 0x44, 0x03, 0x41, 0x10, 0xB3, 0xE1, 0xE6, 0xE6, 0x00, 0x60, 0x36, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x06, 0x80, 0x04, 0x6C, 0x6E, 0x74, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x1F, 0x5E, 0x7E]
cmd_MeterType = [0x7E, 0xA0, 0x19, 0x03, 0x41, 0x32, 0x3A, 0xBD, 0xE6, 0xE6, 0x00, 0xC0, 0x01, 0xC1, 0x00, 0x01, 0x00, 0x00, 0x5E, 0x5B, 0x09, 0xFF, 0x02, 0x00, 0x52, 0x9E, 0x7E]

port_name = 'COM1'  # Change this to the appropriate port name
baudrate = 9600  # Change this to the desired baud rate
timeout = 1  # Change this to the desired timeout value

def init_serial_port(port_name, baudrate=9600, timeout=1):
    try:
        # Create a new serial port object
        serial_port = serial.Serial(port_name, baudrate=baudrate, timeout=timeout)
        # print("Serial port initialized successfully.")
        return serial_port
    except serial.SerialException as e:
        print("Error initializing serial port:", e)
        return None
   
def GetSequenceNumber(nAct):
    global g_RRR, g_SSS
    
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
        cFrameType = (g_RRR << 5) | 0x10  # Receive Sequence
        cFrameType |= g_SSS << 1  # Send Sequence
    elif nAct == 3:
        cFrameType = (g_RRR << 5) | 0x10  # Receive Sequence
        cFrameType |= 0x01  # Send Sequence
        
    return cFrameType
 
def hdlc_SendPacket(hdlcREQframeptr, MAX_SIZE):
    for i in range(Hdlc_OutBuf[2] + 2):
        if i < MAX_SIZE:
            hdlcREQframeptr[i] = Hdlc_OutBuf[i]


def MeterCommandUnciperedIframe(Obiscodes, Fromdate, Todate, MeterDataType):
    OutBuf_Index = 0
    K_SUCCESS = 0
    TAG_GET_REQ = 0xC0
    REQ_GET_NORMAL = 1

    DT_ARRAY = 1
    DT_STRUCTURE = 2
    DT_LONG_UNSIGNED = 18
    DT_OCTET_STRING = 9
    DT_INTEGER = 15
    STRUCT_LENGTH = 0x04

    unciperIframe[OutBuf_Index] = TAG_GET_REQ
    OutBuf_Index += 1
    unciperIframe[OutBuf_Index] = REQ_GET_NORMAL
    OutBuf_Index += 1
    unciperIframe[OutBuf_Index] = 0xC1
    OutBuf_Index += 1
    unciperIframe[OutBuf_Index] = K_SUCCESS
    OutBuf_Index += 1

    for code in Obiscodes:
        unciperIframe[OutBuf_Index] = code
        OutBuf_Index += 1

    if MeterDataType == Metercommands.CMD_LP_DATA:
        unciperIframe[OutBuf_Index] = DT_ARRAY
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x01
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_STRUCTURE
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = STRUCT_LENGTH
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_STRUCTURE
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = STRUCT_LENGTH
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_LONG_UNSIGNED
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = (8 >> 8)
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 8
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_OCTET_STRING
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x06
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index:OutBuf_Index+7] = [0x00, 0x00, 0x01, 0x00, 0x00, 0xFF]
        OutBuf_Index += 7
        unciperIframe[OutBuf_Index] = DT_INTEGER
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x02
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_LONG_UNSIGNED
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index:OutBuf_Index+2] = [0x00, 0x00]
        OutBuf_Index += 2
        unciperIframe[OutBuf_Index] = DT_OCTET_STRING
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x0C
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index:OutBuf_Index+6] = Fromdate[:6]
        OutBuf_Index += 6
        unciperIframe[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = DT_OCTET_STRING
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index] = 0x0C
        OutBuf_Index += 1
        unciperIframe[OutBuf_Index:OutBuf_Index+6] = Todate[:6]
        OutBuf_Index += 6
        unciperIframe[OutBuf_Index:OutBuf_Index+2] = [0x00, 0x00]
        OutBuf_Index += 2

    unciperIframe[OutBuf_Index] = 0x00
    OutBuf_Index += 1

    return OutBuf_Index
def HdlcWrapperEncoding(FrameType, UserInformation, len):
    OutBuf_Index = 0
    HCSlength = 0
    length = 0
    CalcChecksum = 0
    crcBytes = bytearray(2)
    userinfo_index = 0
    FrameFormat_length = bytearray(2)
    ControlField = 0
    LLS = bytearray(4)
    userinformation = None

    Flag = 0x7E  # HDLC_START_END_FLAG
    length += 1  # 1
    serveraddress = 0x03

    length += 1  # 2
    Clientaddress = 0x41  # MR Mode

    if FrameType == Frametypes.SNRM_FRAME:
        length += 1
        ControlField = 0x93
        length += 2
        HCSlength = length

    elif FrameType == Frametypes.INFORMATION_FRAME:
        length += 1
        ControlField = GetSequenceNumber(2)
        GetSequenceNumber(1)
        length += 2
        HCSlength = length
        length += 2
        length += 3
        LLS[0] = 0xE6
        LLS[1] = 0xE6
        LLS[2] = 0x00
        length += len
        userinformation = UserInformation

    elif FrameType == Frametypes.SPECIAL_FRAME:
        length += 1
        ControlField = GetSequenceNumber(2)
        GetSequenceNumber(1)
        length += 2
        HCSlength = length
        length += 2
        LLS[0] = 0xE6
        LLS[1] = 0xE6
        LLS[2] = 0x00
        length += 3
        length += 7  # C0 02 C1 00 00 00 01

    elif FrameType == Frametypes.SUPERVISORY_FRAME:
        length += 1
        ControlField = GetSequenceNumber(3)
        length += 2
        HCSlength = length

    elif FrameType == Frametypes.DISCONNECT_FRAME:
        length += 1
        ControlField = 0x53
        length += 2
        HCSlength = length

    FrameFormat_length[0] = 0xA0  # HDLC_FRAME_FORMAT_WITHOUT_SEGMENTATION
    FrameFormat_length[1] = length + 2  # 7

    Hdlc_OutBuf[OutBuf_Index] = Flag
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = FrameFormat_length[0]
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = FrameFormat_length[1]
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = serveraddress
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = Clientaddress
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = ControlField
    OutBuf_Index += 1

    CalcChecksum = hdlc_ChksumCalculate(0xFFFF, Hdlc_OutBuf[1:HCSlength + 1], HCSlength)
    CalcChecksum ^= 0xFFFF
    Hdlc_OutBuf[OutBuf_Index] = CalcChecksum & 0xFF
    OutBuf_Index += 1
    Hdlc_OutBuf[OutBuf_Index] = (CalcChecksum >> 8) & 0xFF
    OutBuf_Index += 1

    if FrameType == Frametypes.INFORMATION_FRAME:
        Hdlc_OutBuf[OutBuf_Index] = LLS[0]
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = LLS[1]
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = LLS[2]
        OutBuf_Index += 1
        while userinfo_index < len:
            Hdlc_OutBuf[OutBuf_Index] = userinformation[userinfo_index]
            OutBuf_Index += 1
            userinfo_index += 1
        CalcChecksum = hdlc_ChksumCalculate(0xFFFF, Hdlc_OutBuf[1:length + 1], length)
        CalcChecksum ^= 0xFFFF
        Hdlc_OutBuf[OutBuf_Index] = CalcChecksum & 0xFF
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = (CalcChecksum >> 8) & 0xFF
        OutBuf_Index += 1

    if FrameType == Frametypes.SPECIAL_FRAME:
        Hdlc_OutBuf[OutBuf_Index] = LLS[0]
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = LLS[1]
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = LLS[2]
        OutBuf_Index += 1
        # C0 02 C1 00 00 00 01
        Hdlc_OutBuf[OutBuf_Index] = 0xC0
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = 0x02
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = 0xC1
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = 0x00
        OutBuf_Index += 1
        special_counter += 1
        Hdlc_OutBuf[OutBuf_Index] = special_counter
        OutBuf_Index += 1

        CalcChecksum = hdlc_ChksumCalculate(0xFFFF, Hdlc_OutBuf[1:length + 1], length)
        CalcChecksum ^= 0xFFFF
        Hdlc_OutBuf[OutBuf_Index] = CalcChecksum & 0xFF
        OutBuf_Index += 1
        Hdlc_OutBuf[OutBuf_Index] = (CalcChecksum >> 8) & 0xFF
        OutBuf_Index += 1

    Hdlc_OutBuf[OutBuf_Index] = Flag

def MeterCommandFrame(Fromdate, Todate, MeterDataType):
    invocationCounter = 0
    Iframe = bytearray(200)  # Initialize bytearray with size 200, filled with zeros
    MeterCommandframe_index = 0
    iframe = None
    AAD = bytearray(1 + 16 + 128)
    tag_buf = bytearray(50)  # Initialize bytearray with size 50, filled with zeros
    address_size = 1
    severaddress = 1
    clientaddress = 0x41
    FrameType = Frametypes.INFORMATION_FRAME

    OIBS_MSN = bytearray([DATA, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, VALUE])  # MSN
    Obiscode_msn = [OIBS_MSN]

    OIBS_RTC = bytearray([CLOCK, 0, 0, 1, 0, 0, 255, VALUE])  # RTC
    Obiscode_rtc = [OIBS_RTC]

    OIBS_INSTANT = bytearray([PROFILE, 1, 0, 94, 91, 0, 255, VALUE, 0x00])  # INSTANTANEOUS
    Obiscode_instant = [OIBS_INSTANT]

    OIBS_BILLING = bytearray([PROFILE, 1, 0, 98, 1, 0, 255, VALUE, 0x00])  # BILLING
    Obiscode_billing = [OIBS_BILLING]

    OIBS_LOAD = bytearray([PROFILE, 1, 0, 99, 1, 0, 255, VALUE, 0x00])  # BILLING
    Obiscode_load = [OIBS_LOAD]

    if MeterDataType == Metercommands.CMD_METER_SNO:
        MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_msn[ObiscodeIndex], Fromdate, Todate, MeterDataType)
    elif MeterDataType == Metercommands.CMD_METER_RTC:
        MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_rtc[ObiscodeIndex], Fromdate, Todate, MeterDataType)
    elif MeterDataType == Metercommands.CMD_INSTANT_PARAM:
        MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_instant[ObiscodeIndex], Fromdate, Todate, MeterDataType)
    elif MeterDataType == Metercommands.CMD_BILLING_PARAM:
        MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_billing[ObiscodeIndex], Fromdate, Todate, MeterDataType)
    elif MeterDataType == Metercommands.CMD_LP_DATA:
        MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_load[ObiscodeIndex], Fromdate, Todate, MeterDataType)
    
    Iframe[1] = MeterCommandframe_index - 2
    iframe = Iframe

    HdlcWrapperEncoding(FrameType, unciperIframe, MeterCommandframe_index)
    
def send_to_serial(data_to_send):
  serial_port = init_serial_port(port_name, baudrate, timeout)
  if serial_port:
    serial_port.write(data_to_send)
    hex_string = ' '.join(format(x, '02X') for x in data_to_send)
    print("Request :", hex_string)
    
    while True:
      meter_response = serial_port.readline()
      if(len(meter_response))>0:
        hex_response = ' '.join(format(x, '02X') for x in meter_response)
        print("Response :", hex_response)   
        return meter_response 
      else:
        break
  serial_port.close()

def parsing_data():
  data_type = (response_buffer[15])
  match data_type:
    case DLMS_DATA_TYPE.UINT8.value:
        data = response_buffer[16]
        return data
    case default:
        return 
  
def parse_meter_category():
  category = parsing_data()
  if(category == 5 and category == 6):
    ret_value = 1
  else:
    ret_value = 3
  return ret_value
  
def ConnectMRmode():
    bool_check = True
    while bool_check:
        response_buffer = send_to_serial(cmd_Snrm)
        if(response_buffer[0] == 0x7E):
          bool_check = False
          print("SNRM Response Ok")
        else:
          print("SNRM Fail")
    bool_check = True      
    while bool_check:
        response_buffer = send_to_serial(cmd_Aarq)
        if(response_buffer[25] == 0x03 and response_buffer[26] == 0x02 and response_buffer[27] == 0x01 and response_buffer[28] == 0x00):
          bool_check = False
          print("AARQ Ok")
        else:
          print("AARQ Fail")
  
def Read_MeterNumber():
    GetSequenceNumber(0)
    GetSequenceNumber(1)
    MeterCommandFrame(0, 0, Metercommands.CMD_METER_RTC)
    hdlc_SendPacket(LoadREQframeptr);
    response_buffer = send_to_serial(cmd_Aarq)
    print(response_buffer)
  
ConnectMRmode()
Read_MeterNumber()

# response_buffer = send_to_serial(cmd_MeterType)
# meter_phase = parse_meter_category()
# print("meter_phase ",meter_phase)



