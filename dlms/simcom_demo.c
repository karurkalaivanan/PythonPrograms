/**
  ******************************************************************************
  * @file    simcom_demo.c
  * @author  SIMCom OpenSDK Team
  * @brief   Source code for all OpenSDK demo task management with UI.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 SIMCom Wireless.
  * All rights reserved.
  *
  ******************************************************************************
  */

/* Includes ------------------------------------------------------------------*/
#include "simcom_api.h"
#include "string.h"
#include "stdlib.h"
#include "stdio.h"
#include "simcom_demos.h"

#ifdef SIMCOM_UI_DEMO
sMsgQRef urc_mqtt_msgq_1;

///////////////DLMS/////////////////////////
#define COMDELAY 250

#define DATA 1
#define VALUE 2
#define OBIS 3
#define PROFILE 7
#define CLOCK 8

#define MAX_SIZE 150
char g_RRR = 0;
char g_SSS = 0;
char arrqframe_index = 0;

INT8 PhaseType = 0;
char ObiscodeIndex = 0;
char unciperIframe[128] = {0};
//char LoadREQframeptr[MAX_SIZE] = {0};
char MeterSerialNo_Final[] = {0}; // 30-03-2022

char Fromdate[6] = {0};
char Todate[6] = {0};

char *LLS_Keys[8] = {"lnt1",	 // lnt
					"mx201199", // maxwell
					"11111111",
					"ABCD0001",		 // secure
					"1111111111111111", //
					"1A2B3C4D",
					"123456"};
////////////////////////////////////////////

//all demo list
typedef enum
{
    SC_DEMO_FOR_NETWORK             =  1,  //API test for network
    SC_DEMO_FOR_SIMCARD             =  2,  //API test for SIM Card
    SC_DEMO_FOR_SMS                 =  3,  //API test for SMS
    SC_DEMO_FOR_UART                =  4,  //API test for UART
    SC_DEMO_FOR_USB                 =  5,  //API test for USB
    SC_DEMO_FOR_GPIO                =  6,  //API test for GPIO
    SC_DEMO_FOR_PMU                 =  7,  //API test for PMU
    SC_DEMO_FOR_I2C                 =  8,  //API test for I2C
    SC_DEMO_FOR_AUDIO               =  9,  //API test for audio
    SC_DEMO_FOR_FILE_SYSTEM         =  10,  //API test for File System
    SC_DEMO_FOR_TCP_IP              =  11,  //API test for TCP/IP
    SC_DEMO_FOR_HTTP_HTTPS          =  12,  //API test for HTTP(s)
    SC_DEMO_FOR_FTP_FTPS            =  13,  //API test for FTP(s)
    SC_DEMO_FOR_MQTT_MQTTS          =  14,  //API test for MQTT(s)
    SC_DEMO_FOR_SSL                 =  15,  //API test for SSL
    SC_DEMO_FOR_OTA                 =  16,  //API test for OTA
    SC_DEMO_FOR_LBS                 =  17,  //API test for LBS
    SC_DEMO_FOR_NTP                 =  18,  //API test for NTP
    SC_DEMO_FOR_HTP                 =  19,  //API test for HTP
    SC_DEMO_FOR_INTERNET_SERVICE    =  20,  //API test for Internet service
    SC_DEMO_FOR_TTS                 =  21,  //API test for TTS
    SC_DEMO_FOR_CALL                 = 22,  //API test for CALL
    SC_DEMO_FOR_WIFI                =  23,  //API test for WIFI
#ifdef FEATURE_SIMCOM_GPS
    SC_DEMO_FOR_GNSS                =  24,  //API test for GNSS
    SC_DEMO_FOR_LCD                 =  25,  //API test for LCD
#else
    SC_DEMO_FOR_LCD                 =  24,  //API test for LCD
#endif
    SC_DEMO_FOR_RTC                 =  26,  //API test for RTC
    SC_DEMO_FOR_FLASH               =  27,  //API test for flash
#ifdef FEATURE_SIMCOM_FS_OLD
    SC_DEMO_FOR_FILE_SYSTEM_OLD         =  28,  //API test for File System of 1601
#endif
    SC_DEMO_FOR_SPI                 =  29,
    SC_DEMO_FOR_CAM                 =  30,  //API test for CAM
#ifdef BT_SUPPORT
    SC_DEMO_BT = 31,
    SC_DEMO_LE_SERVER = 32,
    SC_DEMO_LE_CLIENT = 33,
#endif
    SC_DEMO_FOR_SPI_NOR = 34,
    SC_DEMO_FOR_APP_DOWNLOAD = 35,
    SC_DEMO_FOR_JAMMING_DETECT = 36,
    SC_DEMO_FOR_WTD = 37,  //API test for WTD
    SC_DEMO_FOR_SPI_NAND = 38,
    SC_DEMO_FOR_ZLIB = 39,
    SC_DEMO_FOR_RSA = 40,  //API test for RSA
    SC_DEMO_FOR_PWM = 41
}SC_DEMO_TYPE;


sMsgQRef simcomUI_msgq;
sTaskRef simcomUIProcesser;
static UINT8 simcomUIProcesserStack[1024 * 30];
extern void NetWorkDemo(void);
extern void SMSDemo(void);
extern void FtpsDemo(void);
extern void TcpipDemo(void);
extern void HttpsDemo(void);
extern void UartDemo(void);
extern void GpioDemo(void);
extern void LbsDemo(void);
extern void SslDemo(void);
extern void MbedTLSDemo(void);
extern void MqttDemo(void);
extern void NtpDemo(void);
extern void HtpDemo(void);
extern void FsDemo(void);
extern void AudioDemo(void);
extern void TTSDemo(void);
extern void CALLDemo(void);
extern void WIFIDemo(void);
extern void FotaDemo(void);
extern void GNSSDemo(void);
extern void LcdDemo(void);
extern void RTCDemo(void);
extern void SimcardDemo(void);
extern void FlashRWdemo(void);
extern void Fs2Demo(void);
extern void PMUDemo(void);
extern void I2cDemo(void);
extern void SpiDemo(void);
extern void SpiNorDemo(void);
extern void SpiNandDemo(void);
extern void CamDemo(void);
#ifdef BT_SUPPORT
extern void sAPP_BTDemo(void);
extern void sAPP_BleServerDemo(void);
extern void LEClientDemo(void);
#endif
extern void AppDownloadDemo(void);
extern void JamDectDemo(void);
extern void WTDDemo(void);
extern void demo_pwm(void);

////////////DLMS Variables////////
#define LNT         1
#define SECURE      2
#define METER_COUNT 3

#define MAX_SIZE 1024

extern int serial_received;

int hdlc_ChksumCalculate(int fcs, char pcp[], int len)
{
	int fcstab[] = {
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
		0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78};

	int i = 0;
	int j = 0;
	for (j = len; j > 0; j--)
	{
		fcs = (int)((fcs >> 8) ^ fcstab[(fcs ^ pcp[i++]) & 0xff]);
	}
	return fcs;
}

enum Frametypes
{
	INFORMATION_FRAME,
	SUPERVISORY_FRAME,
	SNRM_FRAME,
	DISCONNECT_FRAME,
	SPECIAL_FRAME
};

enum Metercommands
{
	CMD_SNRM,
	CMD_AARQ,
	CMD_METER_SNO,
	CMD_METER_TYPE,
	CMD_METER_RTC,
	CMD_INSTANT_PARAM,
  CMD_BILLING_PARAM,
	CMD_LP_DATA,
  CMD_METER_DISC
};

enum profile
{
	meter_sno,
	meter_rtc,
	meter_type,
	meter_nameplate,
	meter_instantaneous,
	meter_blockload,
	meter_dailyload,
	meter_billing,
	meter_event_voltage,
	meter_event_current,
	meter_event_power,
	meter_event_transaction,
	meter_event_other,
	meter_event_nonrollover,
	meter_event_control
};

char Hdlc_OutBuf[255] = {0};
int special_counter = 0;

INT8 ResponseBuffer[1024] = {0};
int res_buffer_length = 0;
int metermake = 0;
int profile = 0;
int sequence_number = 0;
////////////DLMS Variables////////
/**
  * @brief  Print string to UART1 or USB AT port.
  * @param  format,data pointer
  * @note   Please define SIMCOM_UI_DEMO_TO_UART1_PORT or SIMCOM_UI_DEMO_TO_USB_AT_PORT in advance.
  * @retval void
  */
void PrintfResp(INT8* format)
{
    UINT32 length = strlen(format);
#ifdef SIMCOM_UI_DEMO_TO_UART1_PORT
    sAPI_UartWrite(SC_UART2,(UINT8*)format,length);
#else
    sAPI_UsbVcomWrite((UINT8*)format,length);
#endif
}

/**
  * @brief  Print operation menu.
  * @param  options_list,operation list
  * @param  array_size,size of options_list
  * @note   Please define SIMCOM_UI_DEMO_TO_UART1_PORT or SIMCOM_UI_DEMO_TO_USB_AT_PORT in advance.
  * @retval void
  */
void PrintfOptionMenu(INT8* options_list[], int array_size)
{
    UINT32 i = 0;
    sAPI_Debug("array_size = [%d]",array_size);
    INT8 menu[80] = {0};
    PrintfResp("\r\n************************************************************\r\n");
    for(i = 0;i < (array_size/2);i++)
    {
        memset(menu, 0, 80);
        snprintf(menu, 80, "%-30s%-30s", options_list[2*i], options_list[2*i+1]);
        PrintfResp(menu);
        PrintfResp("\r\n");
    }

    if(array_size%2 != 0)
    {
        memset(menu, 0, 80);
        snprintf(menu, 80, "%s", options_list[array_size-1]);
        PrintfResp(menu);
        PrintfResp("\r\n");
    }
    PrintfResp("************************************************************\r\n");

}

/**
  * @brief  Get input operation parameter from UI.
  * @param  void
  * @note   Blocking API,suspend until there is data received from UI shell(UART).
  * @retval void
  */
SIM_MSG_T GetParamFromUart(void)
{
    SIM_MSG_T optionMsg ={0,0,0,NULL};
    sAPI_MsgQRecv(simcomUI_msgq,&optionMsg,SC_SUSPEND);

    return optionMsg;
}

int ClearResponseBuffer()
{
    memset(ResponseBuffer, 0, sizeof(ResponseBuffer));
		return 1;
}

void printdata(char printarray[])
{
    for(int len = 0; len < printarray[2]+2 ; len++)
    {
        sAPI_UartPrintf("%02X ", printarray[len]);//Print UART Receive data in Debug port
    }
}

char MeterCommandUnciperedIframe(char Obiscodes[], char Fromdate[], char Todate[], char MeterDataType)
{
  int i = 0;
  char OutBuf_Index = 0;
  char K_SUCCESS = 0;
	char TAG_GET_REQ = 0xC0;
	char REQ_GET_NORMAL = 1;

	#define DT_ARRAY 1
	#define DT_STRUCTURE 2
	#define DT_LONG_UNSIGNED 18
	#define DT_OCTET_STRING 9
	#define DT_INTEGER 15
	char STRUCT_LENGTH = 0x04;

  unciperIframe[OutBuf_Index++] = TAG_GET_REQ; // 0xC0
  unciperIframe[OutBuf_Index++] = REQ_GET_NORMAL;
  unciperIframe[OutBuf_Index++] = 0xC1; // 0xC1;//HDLCNEGOPARAMS_FORMAT;
  unciperIframe[OutBuf_Index++] = K_SUCCESS;

  unciperIframe[OutBuf_Index++] = Obiscodes[0]; // IC Interface Class
  unciperIframe[OutBuf_Index++] = Obiscodes[1]; // OBIS 1st BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[2]; // OBIS 2nd BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[3]; // OBIS 3rd BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[4]; // OBIS 4th BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[5]; // OBIS 5th BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[6]; // OBIS 6th BYTE
  unciperIframe[OutBuf_Index++] = Obiscodes[7];
	if (MeterDataType == CMD_LP_DATA) 
  {
    unciperIframe[OutBuf_Index++] = (char)DT_ARRAY;
    unciperIframe[OutBuf_Index++] = 0x01; // length of DT_ARRAY
    unciperIframe[OutBuf_Index++] = (char)DT_STRUCTURE;
    unciperIframe[OutBuf_Index++] = 0x04; // length of DT_STRUCTURE
    unciperIframe[OutBuf_Index++] = (char)DT_STRUCTURE;
    unciperIframe[OutBuf_Index++] = STRUCT_LENGTH;
    unciperIframe[OutBuf_Index++] = (char)DT_LONG_UNSIGNED;
    unciperIframe[OutBuf_Index++] = (char)(8 >> 8);
    unciperIframe[OutBuf_Index++] = (char)(8);
    unciperIframe[OutBuf_Index++] = (char)DT_OCTET_STRING;
    unciperIframe[OutBuf_Index++] = 0x06; // length of DT_OCTET_STRING
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0xFF;
    unciperIframe[OutBuf_Index++] = (char)DT_INTEGER;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = (char)DT_LONG_UNSIGNED;
    unciperIframe[OutBuf_Index++] = 0x00; // data index
    unciperIframe[OutBuf_Index++] = 0x00; // data index
    unciperIframe[OutBuf_Index++] = (char)DT_OCTET_STRING;
    unciperIframe[OutBuf_Index++] = 0x0C;        // length of DT_OCTET_STRING9       unciperIframe[OutBuf_Index++] = rload->Fromdate[0];
    unciperIframe[OutBuf_Index++] = (char)Fromdate[0]; // 0x07;
    unciperIframe[OutBuf_Index++] = (char)Fromdate[1]; // 0xE5;
    unciperIframe[OutBuf_Index++] = (char)Fromdate[2]; // 0x0C;
    unciperIframe[OutBuf_Index++] = (char)Fromdate[3]; // 0x04;
    unciperIframe[OutBuf_Index++] = 0x00;
    
    unciperIframe[OutBuf_Index++] = (char)Fromdate[4]; // 0x06 ;//0x05; //rload->Fromdate[4];
    unciperIframe[OutBuf_Index++] = (char)Fromdate[5]; // 0x30;//rload->Fromdate[5];

    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00; 
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = (char)DT_OCTET_STRING;
    unciperIframe[OutBuf_Index++] = 0x0C;      // length of DT_OCTET_STRING
    unciperIframe[OutBuf_Index++] = (char)Todate[0]; // 0x07;
    unciperIframe[OutBuf_Index++] = (char)Todate[1]; // 0xE5;
    unciperIframe[OutBuf_Index++] = (char)Todate[2]; // 0x0C;
    unciperIframe[OutBuf_Index++] = (char)Todate[3]; // 0x04;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = (char)Todate[4]; // 0x06;// 0x01;//rload->Todate[4];
    unciperIframe[OutBuf_Index++] = (char)Todate[5]; // 0x1E;// 0x15;//rload->Todate[5];
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00; 
    unciperIframe[OutBuf_Index++] = 0x00; 
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = (char)DT_ARRAY;
    //unciperIframe[OutBuf_Index++] = 0x00; // length of DT_ARRAY */
  }
	unciperIframe[OutBuf_Index++] = 0x00;
  
  return OutBuf_Index;
}

void MeterCommandFrame(char Fromdate[], char Todate[], char MeterDataType)
{
  int invocationCounter = 0;
  char Iframe[200] = {0};
  char MeterCommandframe_index = 0;
  char *iframe = NULL;
  char AAD[1 + 16 + 128];
  char tag_buf[50] = {0};
  char address_size = 1;
  char severaddress = 1;
  char clientaddress = 0x41;
  char FrameType = INFORMATION_FRAME;

	char OIBS_MSN[] = {DATA, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, VALUE}; /*MSN*/
	
	char *Obiscode_msn[] = { OIBS_MSN };

	char OIBS_RTC[] = {CLOCK, 0, 0, 1, 0, 0, 255, VALUE}; /*RTC*/ 
	
	char *Obiscode_rtc[] = { OIBS_RTC };

	char OIBS_INSTANT[] = {PROFILE, 1, 0, 94, 91, 0, 255, VALUE, 0x00}; /*INSTANTANEOUS*/ 

	char *Obiscode_instant[] = { OIBS_INSTANT};

	char OIBS_BILLING[] = {PROFILE, 1, 0, 98, 1, 0, 255, VALUE, 0x00}; /*BILLING*/ 

	char *Obiscode_billing[] = { OIBS_BILLING};

	char OIBS_LOAD[] = {PROFILE, 1, 0, 99, 1, 0, 255, VALUE, 0x00}; /*BILLING*/ 

	char *Obiscode_load[] = { OIBS_LOAD};
  
	switch (MeterDataType)
	{
	case CMD_METER_SNO:
		MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_msn[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
		break;
	case CMD_METER_RTC:	
		MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_rtc[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
		break;
	case CMD_INSTANT_PARAM:
		MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_instant[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
		break;
	case CMD_BILLING_PARAM:
		MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_billing[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
		break;
	case CMD_LP_DATA:
		MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_load[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
		break;
	default:
		break;
	}
 
  Iframe[1] = MeterCommandframe_index - 2;
  iframe = &Iframe[0];

  HdlcWrapperEncoding(FrameType, unciperIframe, MeterCommandframe_index);
}

char GetSequenceNumber(char nAct)
{
	char cFrameType = 0;
	switch (nAct)
	{
	case 0:
		g_RRR++;
		if (g_RRR > 0x07)
			g_RRR = 0;
		break;
	case 1:
		g_SSS++;
		if (g_SSS > 0x07)
			g_SSS = 0;
		break;
	case 2:
		cFrameType = 0;
		cFrameType = (char)((g_RRR << 5) | 0x10);		// Receive Sequence
		cFrameType = (char)(cFrameType | (g_SSS << 1)); // Send Seqence
		break;
	case 3:
		cFrameType = (char)((g_RRR << 5) | 0x10); // Receive Sequence
		cFrameType = (char)(cFrameType | 0x01);	  // Send Seqence
		break;
	}
	return cFrameType;
}


void HdlcWrapperEncoding(char FrameType, char *UserInformation, const size_t len)
{
	char OutBuf_Index = 0;
	short HCSlength = 0;
	short length = 0;
	int CalcChecksum = 0;
	char crcBytes[2];
	char userinfo_index = 0;
	char FrameFormat_length[2] = {0};
	char ControlField = 0;
	char LLS[4] = {0};
	char *userinformation = {0};

	char Flag = 0x7E; // HDLC_START_END_FLAG;
	length++;		  // 1
	char serveraddress = 0x03;

	length++; // 2
	char Clientaddress = 0x41;// MR Mode

	switch (FrameType)
	{
	case SNRM_FRAME:
		length++;
		ControlField = 0x93;
		length += 2;
		HCSlength = length;
		break;

	case INFORMATION_FRAME:
		length++;
		ControlField = GetSequenceNumber(2);
		GetSequenceNumber(1);
		length += 2;
		HCSlength = length;
		length += 2;
		length += 3;
		LLS[0] = 0xE6;
		LLS[1] = 0xE6;
		LLS[2] = 0x00;
		length += len;
		userinformation = UserInformation;
		break;

	case SPECIAL_FRAME:
		// 7E A0 7 3 41 51 44 81 7E
		length++;
		ControlField = GetSequenceNumber(2);
		GetSequenceNumber(1);
		length += 2;
		HCSlength = length;
		length += 2;
		LLS[0] = 0xE6;
		LLS[1] = 0xE6;
		LLS[2] = 0x00;
		length += 3;
		// C0 02 C1 00 00 00 01
		length += 7;
		break;

	case SUPERVISORY_FRAME:
		length++;
		ControlField = GetSequenceNumber(3);
		length += 2;
		HCSlength = length;
		break;

	case DISCONNECT_FRAME:
		length++;
		ControlField = 0x53;
		length += 2;
		HCSlength = length;
		break;
	}

	FrameFormat_length[0] = 0xA0;		// HDLC_FRAME_FORMAT_WITHOUT_SEGMENTATION;
	FrameFormat_length[1] = length + 2; // 7

	Hdlc_OutBuf[OutBuf_Index++] = Flag;
	Hdlc_OutBuf[OutBuf_Index++] = FrameFormat_length[0];
	Hdlc_OutBuf[OutBuf_Index++] = FrameFormat_length[1];
	Hdlc_OutBuf[OutBuf_Index++] = serveraddress;
	Hdlc_OutBuf[OutBuf_Index++] = Clientaddress;
	Hdlc_OutBuf[OutBuf_Index++] = ControlField;

	CalcChecksum = hdlc_ChksumCalculate(0xFFFF, &Hdlc_OutBuf[1], (short)(HCSlength));
	CalcChecksum ^= 0xFFFF;
	Hdlc_OutBuf[OutBuf_Index++] = CalcChecksum;
	Hdlc_OutBuf[OutBuf_Index++] = (CalcChecksum >> 8);
	if (FrameType == INFORMATION_FRAME)
	{
		Hdlc_OutBuf[OutBuf_Index++] = LLS[0];
		Hdlc_OutBuf[OutBuf_Index++] = LLS[1];
		Hdlc_OutBuf[OutBuf_Index++] = LLS[2];
		while (userinfo_index < len)
		{
			Hdlc_OutBuf[OutBuf_Index++] = userinformation[userinfo_index++];
		}
		CalcChecksum = hdlc_ChksumCalculate(0xFFFF, &Hdlc_OutBuf[1], (short)(length));
		CalcChecksum ^= 0xFFFF;
		Hdlc_OutBuf[OutBuf_Index++] = CalcChecksum;
		Hdlc_OutBuf[OutBuf_Index++] = (CalcChecksum >> 8);
	}
	if (FrameType == SPECIAL_FRAME)
	{
		Hdlc_OutBuf[OutBuf_Index++] = LLS[0];
		Hdlc_OutBuf[OutBuf_Index++] = LLS[1];
		Hdlc_OutBuf[OutBuf_Index++] = LLS[2];
		// while (userinfo_index < len)
		{ // C0 02 C1 00 00 00 01
			Hdlc_OutBuf[OutBuf_Index++] = 0xC0;
			Hdlc_OutBuf[OutBuf_Index++] = 0x02;
			Hdlc_OutBuf[OutBuf_Index++] = 0xC1;
			Hdlc_OutBuf[OutBuf_Index++] = 0x00;
			Hdlc_OutBuf[OutBuf_Index++] = 0x00;
			Hdlc_OutBuf[OutBuf_Index++] = 0x00;
			special_counter = special_counter + 1;
			Hdlc_OutBuf[OutBuf_Index++] = special_counter;
		}
		CalcChecksum = hdlc_ChksumCalculate(0xFFFF, &Hdlc_OutBuf[1], (short)(length));
		CalcChecksum ^= 0xFFFF;
		Hdlc_OutBuf[OutBuf_Index++] = CalcChecksum;
		Hdlc_OutBuf[OutBuf_Index++] = (CalcChecksum >> 8);
	}
	Hdlc_OutBuf[OutBuf_Index] = Flag;
}

void hdlc_SendPacket(char hdlcREQframeptr[MAX_SIZE])
{
	for (int i = 0; i <= Hdlc_OutBuf[2] + 1; i++)
	{
		hdlcREQframeptr[i] = Hdlc_OutBuf[i];
	}
}

int bitRead(number, position)
{
    return (number >> position) & 1;
}
    


int getframelenth( unsigned char x_high, unsigned char x_low)
{
  int combined;
  combined = x_high;              //send x_high to rightmost 8 bits
  combined = combined<<8;         //shift x_high over to leftmost 8 bits
  combined |= x_low;              //logical OR keeps x_high intact in combined and fills in rightmost 8 bits   
  combined &= 0x07FF;             //move 5 byte to get length
 
  return combined;
}

void DateTime2DLMS(char fromDateTime[], char ToDateTime[])
{
  int tempyr = 0;
  char fdtHour[3] = {0}, fdtMin[3] = {0}, fdtSec[3] = {0}, fdtDate[3] = {0}, fdtMonth[3] = {0}, fdtYear[5] = {0};
  char todtHour[3] = {0}, todtMin[3] = {0}, todtSec[3] = {0}, todtDate[3] = {0}, todtMonth[3] = {0}, todtYear[5] = {0};

  sprintf(fdtHour, "%.2s", fromDateTime);    // 17
  sprintf(fdtMin, "%.2s", fromDateTime + 2); // 14

  sprintf(fdtDate, "%.2s", fromDateTime + 4);  // 25
  sprintf(fdtMonth, "%.2s", fromDateTime + 6); // 10
  sprintf(fdtYear, "%.4s", fromDateTime + 8);  // 2017

  sprintf(todtHour, "%.2s", ToDateTime);    // 17
  sprintf(todtMin, "%.2s", ToDateTime + 2); // 14

  sprintf(todtDate, "%.2s", ToDateTime + 4);  // 25
  sprintf(todtMonth, "%.2s", ToDateTime + 6); // 10
  sprintf(todtYear, "%.4s", ToDateTime + 8);  // 2017

  tempyr = atoi(todtYear);
  Todate[0] = (tempyr >> 8);     // 20 YEAR 1
  Todate[1] = (tempyr & 0x00FF); // 17 YEAR 2
  Todate[2] = atoi(todtMonth);   // 11 MONTH
  Todate[3] = atoi(todtDate);    // 22 DAY
  Todate[4] = atoi(todtHour);
  Todate[5] = atoi(todtMin);

  tempyr = atoi(fdtYear);
  Fromdate[0] = tempyr >> 8;
  Fromdate[1] = tempyr & 0x00FF;
  Fromdate[2] = atoi(fdtMonth);
  Fromdate[3] = atoi(fdtDate);
  Fromdate[4] = atoi(fdtHour);
  Fromdate[5] = atoi(fdtMin);
  
	PrintfResp("\nTodate : ");
	for(int len = 0; len < 6 ; len++)
    {
        sAPI_UartPrintf("%02X ", Todate[len]);//Print UART Receive data in Debug port
    }
	PrintfResp("\nFromdate : ");
	for(int len = 0; len < 6 ; len++)
    {
        sAPI_UartPrintf("%02X ", Fromdate[len]);//Print UART Receive data in Debug port
    }
}

void ReadProfileGeneric(char fromDateTime[],char ToDateTime[],int fmetertype)
{
		char LoadREQframeptr[MAX_SIZE] = {0};
		int Block_response = 0;
		int frame_complete = 0;
		int final_block = 0;
		special_counter = 0;
		GetSequenceNumber(0);
		GetSequenceNumber(1);
		DateTime2DLMS(fromDateTime, ToDateTime);
		MeterCommandFrame(Fromdate, Todate, fmetertype);
		hdlc_SendPacket(LoadREQframeptr);
		PrintfResp("\nCommand : ");
		sAPI_UartPrintf("%02X ", fmetertype);
		PrintfResp("\n");
		printdata(LoadREQframeptr);
		sAPI_UartWrite(SC_UART,(UINT8*)LoadREQframeptr, LoadREQframeptr[2]+2);
		sAPI_TaskSleep(COMDELAY);
    //Check block response 
		if (ResponseBuffer[11] == 0xC4)
		{
			if (ResponseBuffer[12] == 0x02)
			{
				Block_response = 1;
			}
		}
		//Check segment_action bit
		int segment_action = bitRead(ResponseBuffer[1],3);
		PrintfResp("\nSegment action ");
    sAPI_UartPrintf("%02X ", segment_action);
		if(Block_response == 1 || segment_action == 1)
		{
			frame_complete = 1;
		}
			
		while(frame_complete)
		{
			int check_A0_frame = bitRead(ResponseBuffer[1],3);
			GetSequenceNumber(0);
			if (check_A0_frame == 0)
			{
				HdlcWrapperEncoding(SPECIAL_FRAME, 0, 0);
				PrintfResp("\nSPECIAL_FRAME ");
			}
			else
			{
				HdlcWrapperEncoding(SUPERVISORY_FRAME, 0, 0);
				PrintfResp("\nSUPERVISORY_FRAME ");
			}

			hdlc_SendPacket(LoadREQframeptr);
			
			printdata(LoadREQframeptr);
			sAPI_UartWrite(SC_UART,(UINT8*)LoadREQframeptr, LoadREQframeptr[2]+2);
			sAPI_TaskSleep(COMDELAY);

			segment_action = bitRead(ResponseBuffer[1],3);
				
				if(Block_response == 0)
				{
					if (segment_action == 0)
					{
						frame_complete = 0;
					}
				}
				else if(Block_response == 1 && final_block == 0)
				{
					if (ResponseBuffer[13] == 0xC1 && ResponseBuffer[14] == 0x01)
					{
						if(segment_action == 0)//A0
						{
							frame_complete = 0;
						}
						else
						{
							final_block = 1;
						}
					}
				}
				else if(final_block == 1)
				{
					if (segment_action == 0)
					{
						frame_complete = 0;
					}
				}
		}
}

int send_cmd_meter(int swcase)
{
	char LoadREQframeptr[MAX_SIZE] = {0};
	int ResByteCount = 0;
	int ChoppedByteCount = 0;
	int i = 0;
	int arrindex = 0;
	char Load_dis_con = 0;
	
	char DLMS_LLS_Capital[] = {0x7E, 0xA0, 0x46, 0x03, 0x41, 0x10, 0xC5, 0xD8, 0xE6, 0xE6, 0x00, 0x60, 0x38, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x08, 0x80, 0x06, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x42, 0x5F, 0x7E};
	char DLMS_LLS_LT[] = {0x7E, 0xA0, 0x44, 0x03, 0x41, 0x10, 0xB3, 0xE1, 0xE6, 0xE6, 0x00, 0x60, 0x36, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x06, 0x80, 0x04, 0x6C, 0x6E, 0x74, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x1F, 0x5E, 0x7E};
	char DLMS_LLS_HPL[] = {0x7E, 0xA0, 0x50, 0x03, 0x41, 0x10, 0xFE, 0x50, 0xE6, 0xE6, 0x00, 0x60, 0x42, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x12, 0x80, 0x10, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0xA5, 0xED, 0x7E};
	char DLMS_LLS_LG[] = {0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x43, 0x8A, 0x7E};
	char DLMS_LLS_SECURE[] = {0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x41, 0x42, 0x43, 0x44, 0x30, 0x30, 0x30, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x8A, 0xC8, 0x7E};
	char DLMS_LLS_GENUS[] = {0x7E, 0xA0, 0x57, 0x03, 0x41, 0x10, 0xDF, 0x07, 0xE6, 0xE6, 0x00, 0x60, 0x49, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x03, 0xA6, 0x0A, 0x04, 0x08, 0x47, 0x4F, 0x45, 0x30, 0x30, 0x30, 0x30, 0x30, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x31, 0x41, 0x32, 0x42, 0x33, 0x43, 0x34, 0x44, 0xBE, 0x17, 0x04, 0x15, 0x21, 0x13, 0x20, 0x00, 0x00, 0x00, 0x00, 0x4D, 0x0A, 0x82, 0xD1, 0x8E, 0x20, 0x47, 0xAB, 0xBD, 0xDB, 0xE9, 0xE2, 0x7C, 0x8B, 0xE9, 0xBE, 0x7E};
	char DLMS_LLS_MAXWELL[] = {0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x6D, 0x78, 0x32, 0x30, 0x31, 0x31, 0x39, 0x39, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x1E, 0x1D, 0xFF, 0xFF, 0x3F, 0xE1, 0x7E}; // MAXWELL 04-04-2022
	char DLMS_DISC[] = {0x7E, 0xA0, 0x07, 0x03, 0x41, 0x53, 0x56, 0xA2, 0x7E};
	char DLMS_MeterType[] = {0x7E, 0xA0, 0x19, 0x03, 0x41, 0x32, 0x3A, 0xBD, 0xE6, 0xE6, 0x00, 0xC0, 0x01, 0xC1, 0x00, 0x01, 0x00, 0x00, 0x5E, 0x5B, 0x09, 0xFF, 0x02, 0x00, 0x52, 0x9E, 0x7E};
   
  serial_received = 0;

  switch (swcase) 
	{
			case CMD_SNRM:
					HdlcWrapperEncoding(SNRM_FRAME, 0, 0);
					hdlc_SendPacket(LoadREQframeptr);
					PrintfResp("\nSNRM_FRAME : ");
					printdata(LoadREQframeptr);
					sAPI_UartWrite(SC_UART,(UINT8*)LoadREQframeptr, LoadREQframeptr[2]+2);
					break;
			
			case CMD_AARQ:
					PrintfResp("\nDLMS_LLS_LT : ");
					printdata(DLMS_LLS_LT);
					sAPI_UartWrite(SC_UART,(UINT8*)DLMS_LLS_LT, DLMS_LLS_LT[2]+2);
					break;
      
			case CMD_METER_TYPE:
					PrintfResp("\nDLMSCommand_MeterType : ");
					printdata(DLMS_MeterType);
					sAPI_UartWrite(SC_UART,(UINT8*)DLMS_MeterType, DLMS_MeterType[2]+2);
					break;

			case CMD_METER_RTC:
					GetSequenceNumber(0);
					GetSequenceNumber(1);
					MeterCommandFrame(0, 0, CMD_METER_RTC);
					hdlc_SendPacket(LoadREQframeptr);
					PrintfResp("\nMeter RTC command : ");
					printdata(LoadREQframeptr);
					sAPI_UartWrite(SC_UART,(UINT8*)LoadREQframeptr, LoadREQframeptr[2]+2);
					break;

			case CMD_METER_SNO:
					GetSequenceNumber(0);
					GetSequenceNumber(1);
					MeterCommandFrame(0, 0, CMD_METER_SNO);
					hdlc_SendPacket(LoadREQframeptr);
					PrintfResp("\nMeter Serial number command : ");
					printdata(LoadREQframeptr);
					sAPI_UartWrite(SC_UART,(UINT8*)LoadREQframeptr, LoadREQframeptr[2]+2);
					break;
			
			case CMD_INSTANT_PARAM:
					//ReadInstantaneousParams();
					ReadProfileGeneric(0,0,CMD_INSTANT_PARAM);
					break;
				
			case CMD_BILLING_PARAM:
					//ReadBillingParams();
					ReadProfileGeneric(0,0,CMD_BILLING_PARAM);
					break;
				
			case CMD_LP_DATA:
					ReadProfileGeneric("000003022024","005903022024",CMD_LP_DATA);
					break;
			
			case CMD_METER_DISC:
					PrintfResp("\nDLMS_DISC : ");
					printdata(DLMS_DISC);
					sAPI_UartWrite(SC_UART,(UINT8*)DLMS_DISC, DLMS_DISC[2]+2);
					sAPI_TaskSleep(COMDELAY);
					break;
			
			default:
					break;
	}

	sAPI_TaskSleep(COMDELAY);
	return 1;
}

void PrintString(INT8* stringvalue)
{
	PrintfResp(stringvalue);
}
void PrintValue(INT8* decimalvalue)
{
	sAPI_UartPrintf("%d ",decimalvalue);
}
void PrintHex(INT8* hexvalue)
{
	sAPI_UartPrintf("%02X ",hexvalue);
}

void ParseMeterCategoryType()
{
  int startColumnIndex = 0; // 16 for HPL and L&T Meters and SECURE //17 for MAXWELL

  if (ResponseBuffer[15] == 0x11)
    startColumnIndex = 16;
  else
    startColumnIndex = 17;

  int MeterCategoryType = ResponseBuffer[startColumnIndex];

  if (MeterCategoryType == 5 || MeterCategoryType == 6) // SINGLE PHASE AC STATIC METERS
  {
    PhaseType = 1;// SINGLE PHASE METERS
  }
  else
  {
    PhaseType = 3; // THREE PHASE METERS
  }
	PrintString("\nMeter PhaseType:");
	PrintValue(PhaseType);
}
int ParseDateTime(void)
{
	t_rtc timeval;
  int monthLen[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  int retTime = -1;
	int startColumnIndex = 17;

  int local_year = (int)((ResponseBuffer[startColumnIndex] << 8) | (ResponseBuffer[startColumnIndex + 1]));
	timeval.tm_year = local_year;
	timeval.tm_mon = ResponseBuffer[startColumnIndex + 2];
	timeval.tm_mday = ResponseBuffer[startColumnIndex + 3];
	timeval.tm_hour = ResponseBuffer[startColumnIndex + 5];
	timeval.tm_min = ResponseBuffer[startColumnIndex + 6];
	timeval.tm_sec = ResponseBuffer[startColumnIndex + 7];

	//timeval.tm_year = timeval.tm_year >= 70 ? (1900 + timeval.tm_year) : (2000 + timeval.tm_year);

	if(((timeval.tm_year%4 == 0) && (timeval.tm_year%100 != 0)) || (timeval.tm_year%400 == 0))
                        monthLen[1] += 1;

	retTime = sAPI_SetRealTimeClock(&timeval);

	if(retTime < 0)
	{
		PrintfResp("\r\n set time failed 1 !\r\n");
		return 0;
	}
	else
	{
		PrintfResp("\r\n set time successed !\r\n");
		return 1;
	}	
}

void ParseSerialNumber()
{
	int startColumnIndex = 15;
	long ParsedMeterSerialNo = 0;
	int temp_MSN_Index = 0;
	INT8 arraysize = ResponseBuffer[startColumnIndex+1];
		
	for (int resColumnIndex = startColumnIndex; resColumnIndex < (res_buffer_length - 3); resColumnIndex++)
	{
			if ((ResponseBuffer[startColumnIndex] == 0x09 || ResponseBuffer[startColumnIndex] == 0x0A) && resColumnIndex >= (startColumnIndex + 2))
			{
				MeterSerialNo_Final[temp_MSN_Index++] = ResponseBuffer[resColumnIndex];
			}
	} 
	
	PrintString("\nMeter Serial Number : ");
	sAPI_UartPrintf("%s ",MeterSerialNo_Final);
}


int read_profile(int profilename)
{
	int ret_case = -1;
	//send_cmd_meter(CMD_METER_DISC);
	send_cmd_meter(CMD_SNRM);
	
	if (serial_received && ResponseBuffer[0] == 0x7E)
	{
		ObiscodeIndex = 0;
		g_RRR = 0;
		g_SSS = 0;
		send_cmd_meter(CMD_AARQ);
	}
	else
	{
		PrintfResp("Check Cable/Meter SNRM failed\n");
		return 0;
	}
	
	if ((ResponseBuffer[25] == 0x03 && ResponseBuffer[26] == 0x02 && ResponseBuffer[27] == 0x01 && ResponseBuffer[28] == 0x00) ||
          (ResponseBuffer[29] == 0x03 && ResponseBuffer[30] == 0x02 && ResponseBuffer[31] == 0x01 && ResponseBuffer[32] == 0x00))
	{
		switch (profilename)
		{
		case meter_rtc:
			send_cmd_meter(CMD_METER_RTC);
			break;

		case meter_type:
			send_cmd_meter(CMD_METER_TYPE);
			break;

		case meter_sno: 
			send_cmd_meter(CMD_METER_SNO);
			break;
		
		case meter_instantaneous:
			send_cmd_meter(CMD_INSTANT_PARAM);
			break;
		
		case meter_billing:
			send_cmd_meter(CMD_BILLING_PARAM);
			break;
		
		case meter_blockload:
			send_cmd_meter(CMD_LP_DATA);
			break;
		
		default:
			break;
		}
	}
	else
	{
		send_cmd_meter(CMD_METER_DISC);
		PrintfResp("Meter AARQ failed\n");
		return 0;
	}
	
	if (serial_received)
	{
		switch (profilename)
		{
		case meter_type:
			ParseMeterCategoryType();
			break;
		
		case meter_sno:
			ParseSerialNumber();
			break;
		
		case meter_rtc:
			ret_case = ParseDateTime();
			if(ret_case < 1)
				send_cmd_meter(CMD_METER_RTC);
			break;
		
		default:
			break;
		}	
		send_cmd_meter(CMD_METER_DISC);		
	}
	else
	{
		PrintfResp("\nMeter TYPE failed");
		return 0;
	}
	return 1;        
}
void setTime()
{
	t_rtc timeval;
  int monthLen[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  int retval = -1;
	
	timeval.tm_year = 23;
	timeval.tm_mon = 02;
	timeval.tm_mday = 01;
	timeval.tm_hour = 15;
	timeval.tm_min = 51;
	timeval.tm_sec = 0;

	timeval.tm_year = timeval.tm_year >= 70 ? (1900 + timeval.tm_year) : (2000 + timeval.tm_year);

	if(((timeval.tm_year%4 == 0) && (timeval.tm_year%100 != 0)) || (timeval.tm_year%400 == 0))
                        monthLen[1] += 1;

	retval = sAPI_SetRealTimeClock(&timeval);
	if(retval < 0)
			PrintfResp("\r\n set time failed 1 !\r\n");
	else
			PrintfResp("\r\n set time successed !\r\n");
}

void setwdtimer()
{
	int ret_timer = -1;

	ret_timer = sAPI_SetWtdTimeOutPeriod(0x60);//feed dog 16S Period is 0x04

	ret_timer |=sAPI_FalutWakeEnable(1);

	ret_timer |=sAPI_SoftWtdEnable(1);

	ret_timer |=sAPI_FeedWtd();
}

void PrintTime()
{
		t_rtc timeval;
		char buff[100] = {0};

		sAPI_GetRealTimeClock(&timeval);
		sprintf(buff,"\r\n Get RTC time: %d/%02d/%02d,%02d:%02d:%02d \r\n", timeval.tm_year, timeval.tm_mon, timeval.tm_mday,
				timeval.tm_hour, timeval.tm_min, timeval.tm_sec);
		PrintfResp(buff);
}
/**
  * @brief  SIMCom UI demo processer.
  * @param  arg
  * @note   Please select demo according to CLI.
  * @retval void
  */
void sTask_SimcomUIProcesser(void * arg)
{
		int ret = -1;
    sAPI_TaskSleep(200);
    PrintfResp("DLMS PART 1");
		int loopback = 0;
    //TcpipDemo(); 
    // serial_received = 1;
    // sequence_number = 0; 
		char  pTemBuffer[512*3];
	  INT64 total_size = sAPI_GetSize("C:/");
    INT64 free_size = sAPI_GetFreeSize("C:/");
    INT64 used_size = sAPI_GetUsedSize("C:/");
    sprintf(pTemBuffer, "\r\n FILE SYSTEM Total_size= %lld, Free_size= %lld,used_size = %lld\r\n",total_size, free_size,used_size);
    sAPI_UartPrintf(pTemBuffer);
    //setwdtimer().
    //setTime();   
    while(1)
    {
			  //ret = sAPI_FeedWtd();
	
        sAPI_TaskSleep(200);

				while(1)
				{
					ret = read_profile(meter_rtc);
					if(ret > 0)
					{
						PrintfResp("\n RTC read successfully");
						break;
					}
					else
					{
						loopback++;
						if(loopback > 10)
						{
							PrintfResp("\n RTC read failed");
							break;
						}
					}
				}
				
				PrintTime();

				ret = read_profile(meter_type);
				if(ret > 0)
				{
					PrintfResp("\n Meter Type read successfully");
				}

				PrintTime();

				ret = read_profile(meter_sno);
				if(ret > 0)
				{
					PrintfResp("\n Meter Serial Number read successfully");
				}
				
				PrintTime();

				ret = read_profile(meter_instantaneous);
				if(ret > 0)
				{
					PrintfResp("\n Instant profile read successfully");
				}
				
				PrintTime();

				ret = read_profile(meter_billing);
				if(ret > 0)
				{
					PrintfResp("\n Instant profile read successfully");
				}

				PrintTime();

				ret = read_profile(meter_blockload);
				if(ret > 0)
				{
					PrintfResp("\n Block profile read successfully");
				}
    }

}

/**
  * @brief  Create SIMCom UI demo task.
  * @param  void
  * @note   UI demo based on message(queue) with blocking method.
  * @retval void
  */
void sAPP_SimcomUIDemo(void)
{
    SC_STATUS status;
    status = sAPI_MsgQCreate(&simcomUI_msgq, "simcomUI_msgq", sizeof(SIM_MSG_T), 12, SC_FIFO);
    if(SC_SUCCESS != status)
    {
        sAPI_Debug("msgQ create fail");
    }

	status = sAPI_MsgQCreate(&urc_mqtt_msgq_1, "urc_mqtt_msgq_1", (sizeof(SIM_MSG_T)), 4, SC_FIFO);        //msgQ for subscribed data transfer
     if(status != SC_SUCCESS)
    {
        sAPI_Debug("message queue creat err!\n");
    }

    status = sAPI_TaskCreate(&simcomUIProcesser,simcomUIProcesserStack,1024 * 30,100,"simcomUIProcesser",sTask_SimcomUIProcesser,(void *)0);
    if(SC_SUCCESS != status)
    {
        sAPI_Debug("task create fail");
    }
}
#endif

