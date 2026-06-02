/*********************************************
 * History :
 * 4G and Metering part is combined on 16-Dec-2022
 * Milestone 1 - Instant data creation and posting to server done
 * Error log file creation
 * brach created
 * autodetection modified
 * Last modified on 05-Jul-2023 17:26
 *************************************************************************************/
#include "LittleFS.h"
#include <time.h> //Version 5.2
#include <ESP32Time.h>

#include "FS.h"

#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>

#include <Update.h>

///////////////////4G//////////////////////////
#include <esp_task_wdt.h>
#include <rom/rtc.h>
///////////////////4G//////////////////////////
#define TRUE 1
#define FALSE 0
#define METER_DEBUG TRUE
///////////////////////////4G///////////////////////////////
#define FORMAT_LittleFS_IF_FAILED true
#define WDT_TIMEOUT 3600
#define MODULE_RESET_4G 19
#define MODULE_RESET_ESP 23
#define RS232_INDICATOR 14
#define DATA_COMMUNICATION 26
#define FOURG_COMMUNICATION 27
#define OTA_STATUS 26
#define U_FLASH 0
#define debug_flag 0
#define RX_BUFFER_MAX 1068
///////////////////////////4G///////////////////////////////

// AESLib aesLib;
char load_array[4] = {0};
char instant_array[4] = {0};
char billing_array[4] = {0};
int special_counter = 0;
// int special_frame = 0;
String plaintext = "HELLOWORLD";
char ssidbuff[20] = {0};
char passwordbuff[30] = {0};
char passwordbuff2[8] = {0};
String global_frame = "";
int g_frame_length = 0;
// AES Encryption Key
byte aes_key[] = {0xBD, 0x17, 0xBB, 0x34, 0xBB, 0x22, 0x12, 0x6F, 0xE8, 0x88, 0xFF, 0x99, 0xA1, 0xDA, 0x17, 0xF4};
// General initialization vector (you must use your own IV's in production for full security!!!)
// byte aes_iv[N_BLOCK] = {0xAF, 0xBC, 0xDA, 0xEE, 0x89, 0x78, 0x77, 0x67, 0x76, 0x56, 0x45, 0x35, 0x12, 0x28, 0xAE, 0x0A};

WebServer server(80);
int command_available = 0;
///////////////MAXIMUM While loop count///////////////////

#define COUNT_BILL 160
#define COUNT_INST 30  //previously it was given as 20 but some obis gives more than 20 packets
#define COUNT_LP 10

#define SOFTWARE_VERSION 2.01

#define LENGTH 0x00
#define AARQ_APPCONTEXT 0xA1
#define AARQ_ACSE_REQS 0x8A
#define AARQ_ACSE_REQ_LEN 0x02
#define AARQ_AUTHMECHNAME 0x8B
#define AARQ_AUTHVALUE 0xAC
#define AARQ_USER_INFO 0xBE
#define TAG_GET_REQ_NORMAL 0x01
#define AARQ_XDLMS_DEDICATED_KEY 0x00
#define AARQ_XDLMS_RESPONSE_ALLOWED 0x00
#define AARQ_XDLMS_QOS 0x00
#define DLMS_VERSION 0x06
#define AARQ_CONFORMANCE 0x5F
#define AARQ_CONFORMANCE_OLD 0x1F
#define ENCRYPTION_ONLY 0x20

#define DT_ARRAY 1
#define DT_STRUCTURE 2
#define DT_LONG_UNSIGNED 18
#define DT_OCTET_STRING 9
#define DT_INTEGER 15

#define LT 0
#define MAXWELL 1
#define LG 2
#define SECURE 3
#define HPL 4
#define GENUS 5
#define CAP 6
#define EEPL 7


#define SINGLE_PH_PARAM_COUNT 9
#define THREE_PH_PARAM_COUNT 9
#define ASSC_REQ_COUNT 3
#define MAX_SIZE 150
#define MAX_SIZE_RESPONSE_BUFFER 540
#define METER_RTC_READ_REQ_COUNT 1
#define TOTAL_NO_OF_KEYS 8
//////////////ADDED///////////////////////////
#define RES_FRAME_COUNT 100

#define FRAME_INST_SNRM 0
#define FRAME_INST_AARQ 1
#define FRAME_INST_RTC 2
#define FRAME_INST_PCT 3
#define FRAME_INST_VECNT 4
#define FRAME_INST_CECNT 5
#define FRAME_INST_PECNT 6
#define FRAME_INST_TECNT 7
#define FRAME_INST_OECNT 8
#define FRAME_INST_NECNT 9
#define FRAME_INST_MSN 10

unsigned int profile_capture_time = 0;
unsigned int profile_ve_count = 0;
unsigned int profile_ce_count = 0;
unsigned int profile_pe_count = 0;
unsigned int profile_te_count = 0;
unsigned int profile_oe_count = 0;
unsigned int profile_ne_count = 0;
int return_value = 0;

int meter_type = 0;
/////////////ADDED//////////////////////////////
// #define
char Hdlc_OutBuf[255] = {0};

enum Frametypes
{
  INFORMATION_FRAME,
  SUPERVISORY_FRAME,
  SNRM_FRAME,
  DISCONNECT_FRAME,
  SPECIAL_FRAME
};
char Fromdate[6] = {0};
char Todate[6] = {0};
char arrqframe_index = 0;
char TAG_AARQ = 0x60;
char AARQFrame[128] = {0};
char app_ctxt_name_1[] = {AARQ_APPCONTEXT, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01};
char aARQ_aCSE_rEQs[] = {AARQ_ACSE_REQS, AARQ_ACSE_REQ_LEN, 0x07, 0x80};
char auth_mech_name_1[] = {AARQ_AUTHMECHNAME, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01};
////////////////////////////////////////////////////////////////////////
int bavailflag = 1;
int availbillentry = 0;
char readentrycount[] = {0x00};
char readendcount[] = {0x00};

//////////////////////////////////////////////////////
int buildid = 11;

String LLS_Keys[TOTAL_NO_OF_KEYS] = {"lnt1",   // lnt
                   "mx201199", // maxwell
                   "11111111", // LNG 
                   "ABCD0001",     // secure
                   "1111111111111111", // HPL
                   "1A2B3C4D", // GENUS
                   "123456", // CAP
                   "ABCDEFGH"}; // EEPL

                   

char auth_password_or_public_Tag_len[] = {AARQ_USER_INFO, 0x02 + 0x0E, 0x04, 0x0E};
char xDlmsRequest1[] = {TAG_GET_REQ_NORMAL, AARQ_XDLMS_DEDICATED_KEY, AARQ_XDLMS_RESPONSE_ALLOWED, AARQ_XDLMS_QOS, DLMS_VERSION, AARQ_CONFORMANCE, AARQ_CONFORMANCE_OLD, 0x04, 0x00, 0x00, 0x1E, 0x1D, 0xFF, 0xFF};

char Obiscode4[] = {0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x02, 0x00};
char *Obiscode[] =
  {Obiscode4};
char Obiscode8[] = {0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x02, 0x00};
char *Obiscode_instant[] =
  {Obiscode8};
char Obiscode12[] = {0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x02}; // Billing DATA
char *Obiscode_billing[] =
  {Obiscode12};
char obis_instantscalar[] = {0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x02, 0x00};
char *Obiscode_InstantScalar[] = 
  {obis_instantscalar};
char obis_loadprofilescalar[] = {0x07, 0x01, 0x00, 94, 0x5B, 0x04, 0xFF, 0x02, 0x00};
char *Obiscode_loadprofileScalar[] = 
  {obis_loadprofilescalar};
///////////////////////////////////////////////////////////////////////////////////
char obis_loaddataobis[] = {0x07, 0x01, 0x00, 99, 0x01, 0x00, 0xFF, 0x03, 0x00};
char *Obiscode_loaddataobis[] = 
  {
    obis_loaddataobis
  };

char obis_loadscalarobis[] = {0x07, 0x01, 0x00, 94, 91, 0x04, 0xFF, 0x03, 0x00};
char *Obiscode_loadscalarobis[] = 
  {
    obis_loadscalarobis
  }; 

char obis_instantdataobis[] = {0x07, 0x01, 0x00, 94, 91, 0x00, 0xFF, 0x03, 0x00};
char *Obiscode_instantdataobis[] = 
  {
    obis_instantdataobis
  }; 

char obis_instantscalarobis[] = {0x07, 0x01, 0x00, 94, 91, 0x03, 0xFF, 0x03, 0x00};
char *Obiscode_instantscalarobis[] = 
  {
    obis_instantscalarobis
  }; 

char obis_billingdataobis[] = {0x07, 0x01, 0x00, 98, 0x01, 0x00, 0xFF, 0x03, 0x00};
char *Obiscode_billingdataobis[] = 
  {
    obis_billingdataobis
  }; 

char obis_billingscalarobis[] = {0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x03, 0x00};
char *Obiscode_billingscalarobis[] = 
  {
    obis_billingscalarobis
  }; 
char obis_eventscalar[] = {0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x02, 0x00};
char *Obiscode_eventscalar[] = 
  {
    obis_eventscalar
  }; 
char obis_eventdataobis[] = {0x07, 0x00, 0x00, 99, 98, 0x01, 0xFF, 0x03, 0x00};
char *Obiscode_eventdataobis[] = 
  {
    obis_eventdataobis
  };   
char obis_eventscalarobis[] = {0x07, 0x01, 0x00, 94, 91, 0x07, 0xFF, 0x03, 0x00};
char *Obiscode_eventscalarobis[] = 
  {
    obis_eventscalarobis
  }; 
//Daily load obis 1.0.99.2.0.255
char obis_dlobis[] = {0x07, 0x01, 0x00, 99, 0x02, 0x00, 0xFF, 0x03, 0x00};
char *Obiscode_dlobis[] = 
  {
    obis_dlobis
  }; 
char obis_dldata[] = {0x07, 0x01, 0x00, 99, 0x02, 0x00, 0xFF, 0x02, 0x00};
char *Obiscode_dldata[] = 
  {
    obis_dldata
  }; 
//Daily load scalar 1.0.94.91.5.255
char obis_dlscalarobis[] = {0x07, 0x01, 0x00, 94, 91, 5, 0xFF, 0x03, 0x00};
char *Obiscode_dlscalarobis[] = 
  {
    obis_dlscalarobis
  }; 
char obis_dlscalardata[] = {0x07, 0x01, 0x00, 94, 91, 5, 0xFF, 0x02, 0x00};
char *Obiscode_dlscalardata[] = 
  {
    obis_dlscalardata
  }; 
////////////////////////////////////////////////////////////////////////////////////////

char ObiscodeIndex = 0;
char TAG_GET_REQ = 0xC0;
char REQ_GET_NORMAL = 1;
char unciperIframe[128] = {0};
char STRUCT_LENGTH = 0x04;
char HDLC_Logical_Name = 0x00;
int incomingByte = 0;
char g_RRR = 0;
char g_SSS = 0;
char INST_Obiscode1[] = {0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0xFF, 0x02};     /*RTC*/
char INST_Obiscode2[] = {0x01, 0x01, 0x00, 0x00, 0x08, 0x04, 0xFF, 0x02};     // Captured period
char INST_Obiscode3[] = {0x07, 0x00, 0x00, 99, 98, 0, 0xFF, 0x07};          // voltage event occured count
char INST_Obiscode4[] = {0x07, 0x00, 0x00, 99, 98, 1, 0xFF, 0x07};          // current event occured count
char INST_Obiscode5[] = {0x07, 0x00, 0x00, 99, 98, 2, 0xFF, 0x07};          // power event occured count
char INST_Obiscode6[] = {0x07, 0x00, 0x00, 99, 98, 3, 0xFF, 0x07};          // transaction event occured count
char INST_Obiscode7[] = {0x07, 0x00, 0x00, 99, 98, 4, 0xFF, 0x07};          // other event occured count
char INST_Obiscode8[] = {0x07, 0x00, 0x00, 99, 98, 5, 0xFF, 0x07};          // non roll over event occured count
char INST_Obiscode9[] = {0x01, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, 0x02}; /*MSN*/ // 30-03-2022

char *INST_Obiscode[] =
  {
    INST_Obiscode1,
    INST_Obiscode2,
    INST_Obiscode3,
    INST_Obiscode4,
    INST_Obiscode5,
    INST_Obiscode6,
    INST_Obiscode7,
    INST_Obiscode8,
    INST_Obiscode9
  };


char OBC_EventVoltage_DATA[] = {0x07, 0x00, 0x00, 99, 98, 0, 0xFF, 0x02};
char *Obiscode_eventvoltage[] =
  {
    OBC_EventVoltage_DATA
  };

char OBC_EventCurrent_DATA[] = {0x07, 0x00, 0x00, 99, 98, 1, 0xFF, 0x02};
char *Obiscode_eventcurrent[] =
  {
    OBC_EventCurrent_DATA
  };

  char OBC_EventPower_DATA[] = {0x07, 0x00, 0x00, 99, 98, 2, 0xFF, 0x02};
char *Obiscode_eventpower[] =
  {
    OBC_EventPower_DATA
  };

  char OBC_EventTransaction_DATA[] = {0x07, 0x00, 0x00, 99, 98, 3, 0xFF, 0x02};
char *Obiscode_eventtransaction[] =
  {
    OBC_EventTransaction_DATA
  };

char OBC_EventOther_DATA[] = {0x07, 0x00, 0x00, 99, 98, 4, 0xFF, 0x02};
char *Obiscode_eventother[] =
  {
    OBC_EventOther_DATA
  };

char OBC_EventNonrollover_DATA[] = {0x07, 0x00, 0x00, 99, 98, 5, 0xFF, 0x02};
char *Obiscode_eventnonrollover[] =
  {
    OBC_EventNonrollover_DATA
  };


char OBC_BILL_SCALAR[] = {0x07, 0x01, 0x00, 94, 91, 0x06, 0xFF, 0x02}; // SCALAR DATA
char *Obiscode_Billscalar[] =
  {
    OBC_BILL_SCALAR};

// bool Get_Scalar_Flag = false;

enum MeterDataTypes
{
  METERCONFIG_DATA,
  LOAD_PROFILE_DATA,
  LOAD_PROFILE_SCALAR,
  INSTANT_DATA,
  INSTANTSCALAR,
  BILLING_DATA,
  BILLINGSCALAR,
  EVENTVOLTAGE,
  EVENTCURRENT,
  EVENTPOWER,
  EVENTTRANSACTION,
  EVENTOTHER,
  EVENTNONROLL,
  LOAD_DATA_OBIS,
  LOAD_SCALAR_OBIS,
  INSTANT_DATA_OBIS,
  INSTANT_SCALAR_OBIS,
  BILLING_DATA_OBIS,
  BILLING_SCALAR_OBIS,
  EVENT_SCALAR_OBIS,
  EVENT_SCALAR,
  EVENT_DATA_OBIS,
  DAILY_LOAD_DATA,
  DAILY_LOAD_OBIS,
  DL_SCALAR_DATA,
  DL_SCALAR_OBIS
};

int PhaseType = 0;
enum PhaseTypes
{
  SINGLE_PHASE = 1,
  THREE_PHASE = 3
};

char THREE_PH_INST_Obiscode1[] = {0x08, 0x00, 0x00, 0x01, 0x00, 0x00, 0xFF, 0x02};     /*RTC*/
char THREE_PH_INST_Obiscode2[] = {0x01, 0x01, 0x00, 0x00, 0x08, 0x04, 0xFF, 0x02};     // Captured period
char THREE_PH_INST_Obiscode3[] = {0x07, 0x00, 0x00, 99, 98, 0, 0xFF, 0x07};          // voltage event occured count
char THREE_PH_INST_Obiscode4[] = {0x07, 0x00, 0x00, 99, 98, 1, 0xFF, 0x07};          // current event occured count
char THREE_PH_INST_Obiscode5[] = {0x07, 0x00, 0x00, 99, 98, 2, 0xFF, 0x07};          // power event occured count
char THREE_PH_INST_Obiscode6[] = {0x07, 0x00, 0x00, 99, 98, 3, 0xFF, 0x07};          // transaction event occured count
char THREE_PH_INST_Obiscode7[] = {0x07, 0x00, 0x00, 99, 98, 4, 0xFF, 0x07};          // other event occured count
char THREE_PH_INST_Obiscode8[] = {0x07, 0x00, 0x00, 99, 98, 5, 0xFF, 0x07};          // non roll over event occured count
char THREE_PH_INST_Obiscode9[] = {0x01, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, 0x02}; /*MSN*/ // 30-03-2022

char *THREE_PH_INST_Obiscode[] =
  {
    THREE_PH_INST_Obiscode1,
    THREE_PH_INST_Obiscode2,
    THREE_PH_INST_Obiscode3,
    THREE_PH_INST_Obiscode4,
    THREE_PH_INST_Obiscode5,
    THREE_PH_INST_Obiscode6,
    THREE_PH_INST_Obiscode7,
    THREE_PH_INST_Obiscode8,
    THREE_PH_INST_Obiscode9
    
  };
// char Meter_RTC_REQframeptr[4][MAX_SIZE];
char ResponseBuffer[RES_FRAME_COUNT][MAX_SIZE_RESPONSE_BUFFER] = {0};
ESP32Time rtc;
int MeterCategoryType = 0;
// char FileBuffer[31][MAX_SIZE];
char Chopped_Inst_DataBuffer[256] = {0};
char Chopped_Inst_Scalar_DataBuffer[256] = {0}; // 14-04-2022
char Chopped_Load_DataBuffer[512] = {0};
// char Combined_DataBuffer[1024];

long ParsedMeterSerialNo = 0;  // 30-03-2022
String MeterSerialNo_Final = ""; // 30-03-2022

String BlockIDs[] = {"00|00", "00|01", "00|02", "00|03", "00|04", "00|05", "00|06", "00|07", "00|08", "00|09", "00|10", "00|11", "00|12",
           "00|13", "00|14", "00|15", "00|16", "00|17", "00|18", "00|19", "00|20", "00|21", "00|22", "00|23"}; // 30-03-2022
String BlockIDs_Buffer[24] = {"0"};                                            // 30-03-2022
// String BlockIDsFileName = "";//30-03-2022
// char temp_Char_Array[4] = {0};//04-04-2022

/*SOFTWARE RTC RELATED VALRIABLES*/
long timeNow = 0;
long timeLast = 0;

// Time start Settings:
int g_startingHour = 0; // set your starting hour here, not below at int hour. This ensures accurate daily correction of time
int g_seconds = 0;
int g_ActualSeconds = 0;
int g_minutes = 0;
int g_hours = 0;
int g_days = 0;
int g_day = 0;
int g_month = 0;
int g_year = 0;

// Accuracy settings
int g_dailyErrorFast = 0; // set the average number of milliseconds your microcontroller's time is fast on a daily basis
int g_dailyErrorBehind = 0; // set the average number of milliseconds your microcontroller's time is behind on a daily basis

int g_correctedToday = 1; // do not change this variable, one means that the time has already been corrected today for the error in your boards crystal. This is true for the first g_day because you just set the time when you uploaded the sketch.
/*SOFTWARE RTC RELATED VALRIABLES*/

bool reset_flag = false;
int METER_MAKE = 0;

// relay operation variables
uint8_t GPIO_Pin = 2;
uint8_t RELAY_ON = 12;
uint8_t RELAY_OFF = 13;

int CYCLE_TIME_IN_MINS = 59;

int resume_reading_instant = 0;
int resume_reading_load = 0;
int resume_reading_gsm = 0;
int is_reading_interrupted = 0;

String global_NodeID = "";

// Version 3 Block
byte kWhValueBytes[10] = {0x00};
byte kWhScalarBytes[10] = {0x00};
byte ProfileCaptureBytes[10] = {0x00};
byte ProfileVEBytes[10] = {0x00};
byte ProfileCEBytes[10] = {0x00};
byte ProfilePEBytes[10] = {0x00};
byte ProfileOEBytes[10] = {0x00};
byte ProfileTEBytes[10] = {0x00};
byte ProfileNEBytes[10] = {0x00};

const int DT_DOUBLE_LONG = 5;
const int DT_DOUBLE_LONG_UNSIGNED = 6;

const byte Active_Power = 27;
const byte Apparent_Power = 28;
const byte Reactive_Power = 29;
const byte Active_Energy = 30;
const byte Apparent_Energy = 31;
const byte Reactive_Energy = 32;
// Version 3 Block

#define LITTLEFS_MOUNT true

////////////OTA VARIABLES///////////////////
int packetcnt = 0;
////////////////////////////////////////////

const char *ssid_wifidownload = "Airtel_9986025401";
const char *password = "air72052";

///////////////////////4G////////////////////////////
int globalfsize = 0, AT_success = 0, exitCount = 0, firmware = 0;
float gw_current_firmware_version = 8.2; // 6.4;

volatile int soft_reset_count = 0;
String GWID = "NSGW000000"; //"NSGW001630";//1501
String password_aes = "";
// char pwd[] = "12345678";
String ssid[50] = {""};
String gw_otaurl[5] = {""};
String nodeotaurl = "";
int fileCount = 1, postSuccess = 0, getSuccess = 0, cfc = 0, global_range = 0, module_reset_count = 0;
String g_filename = "/completefile";
String FourGresponse = "e";
// char ssidbuff[20] = {0};
//  char passwordbuff[300] = {0};
unsigned long lastMillis;
String ciccid = "";
String simeino = "";
String command_data[100] = {""};
/// global variables
char LoadREQframeptr[RES_FRAME_COUNT][MAX_SIZE] = {0};
// int meter_phase = 0;
String secretkey = "tl2CxESUsQsQNNspCY4GHw";

////////////////////////AT COMMANDS LIST DECLARATION/////////////

const char *AT_COMMAND[] = {
  "AT|OK|3000",                                  // 1
  "AT+CPIN?|OK|2000",                                // 2
  "AT+CSQ|OK|2000",                                // 3
  "AT+CREG?|0,1|5000",                               // 4
  "AT+CGREG?|0,1|5000|",                               // 5
  "AT+CGDCONT=1,\"IPV4V6\",\"airtelm2m.com.MNC045.MCC404.GPRS\"|OK|2000",      // 6
  "AT+CMEE=1|OK|3000",                               // 7
  "AT+CGATT=1|OK|3000",                              // 8
  "AT+CGACT=1,1|OK|9000",                              // 9
  "AT+CPSI?|OK|9000",                                // 10
  "AT+CICCID|OK|3000",                               // 11                                                                 //27
  "AT+SIMEI?|OK|3000",                               // 12
  "AT+HTTPINIT|OK|2000",                               // 13
//  "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/gettime?gwid=",     
  "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:16006/gettime?gwid=",       // 14
// 14
  "AT+HTTPPARA=\"CONTENT\",\"application/x-www-form-urlencoded\"|OK|2000",     // 15
  "AT+HTTPACTION=0|OK|10000",                            // 16
  "AT+HTTPHEAD|200 OK|5000",                             // 17
  "AT+HTTPREAD=2000|OK|3000",                            // 18
  "AT+HTTPTERM|OK|2000",                               // 19
  "AT+HTTPINIT|OK|2000",                               // 20
//  "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/senddata\"|OK|2000",    // 21  //change port to 9871 from 9837
  "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:16006/v2/senddata\"|OK|2000",    // 21  //change port to 9871 from 9837

  "AT+HTTPPARA=\"CONTENT\",\"APPLICATION/JSON\"|OK|2000",              // 22
  "AT+HTTPDATA=",                                  // 23
  "AT+HTTPACTION=1|OK|10000",                            // 24
  "AT+HTTPHEAD|200 OK|5000",                             // 25
  "AT+HTTPREAD=2000|OK|3000",                            // 26
  "AT+HTTPTERM|OK|2000",                               // 27
  "AT+HTTPPARA=\"URL\",\"http://configurations.ms-tech.in:6831/sendnodelist_v2\"|OK|2000",  // 28  //change port to 9871 from 9837
  "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/gatewaymemoryfull?gwid=",      // 29
  "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/sendfilelist\"|OK|2000",       // 30  //change port to 9871 from 9837
  "AT+FSDEL=*.*\r\n",                                // 31
  "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:18002/sendcommandstatus\"|OK|2000", // 32
  "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:18002/clearingcommands\"|OK|2000" ,  // 33
  "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/sendtestdata\"|OK|2000"
};

const char *OTA_COMMANDS[] = {
  "AT+FSDEL=*.*|OK|5000",                                 // 0
  "AT+HTTPINIT|OK|2000",                                // 1
  "AT+HTTPPARA=\"URL\",\"",                             // 2
  "AT+HTTPPARA=\"CONTENT\",\"application/x-www-form-urlencoded\"|OK|2000",    // 3
  "AT+HTTPACTION=1|OK|15000",                             // 4
  "AT+HTTPHEAD|200 OK|5000",                              // 5
  "AT+HTTPREADFILE=\"",                             // 6
  "AT+HTTPTERM|OK|2000"                               // 7
};

const char *AT_COMMANDS_FILETRANSFER[] = {
    "AT+FSDEL=*.*|OK|2000",   //0
    "AT+FSMEM|OK|2000",    // 1
    "AT+CFTRXBUF=1|OK|2000", // 2
    "AT+CFTRANRX=",      // 3
    "AT+FSLS|OK|3000",     // 4
    "AT+FSMEM|OK|2000"     // 5
  };

const char *AT_COMMANDS_POSTFILE[] = {
    "AT+HTTPINIT|OK|2000",                  // 0
    "AT+HTTPPARA=\"URL\"",                  // 1
    "AT+HTTPPARA=\"CONTENT\",\"APPLICATION/JSON\"|OK|2000", // 2
    "AT+HTTPPOSTFILE=\"",                 // 3
    "AT+HTTPHEAD|200 OK|2000",                // 4
    "AT+HTTPREAD=2000|OK|3000",               // 5
    "AT+HTTPTERM|OK|2000",                  // 6
    "AT+FSMEM|OK|2000"                    // 7
  };
  
////////////////////////////////////////////////////////////////////////////////////////////

  
bool ReadInstantProfileData()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

    while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(INSTANT_DATA);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    //return CreateInstantDataFile(3, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
    return CreateIPLDataFile(INSTANT_DATA, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}
bool ReadBillingScalarData()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(BILLINGSCALAR);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(BILLINGSCALAR, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadLoadProfileScalar()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(LOAD_PROFILE_SCALAR);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(LOAD_PROFILE_SCALAR, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

///////////////////////////////////////////////////////////////////////////////////////////

bool ReadLoadDataObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(LOAD_DATA_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(LOAD_DATA_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadLoadScalarObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(LOAD_SCALAR_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(LOAD_SCALAR_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadInstaDataObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(INSTANT_DATA_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(INSTANT_DATA_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}



bool ReadInstaScalarObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(INSTANT_SCALAR_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(INSTANT_SCALAR_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadBillingDataObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(BILLING_DATA_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(BILLING_DATA_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadBillingScalarObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(BILLING_SCALAR_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(BILLING_SCALAR_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadEventScalarObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(EVENT_SCALAR_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(EVENT_SCALAR_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadEventScalar()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
  
    Load_ChoppedByteCount = read_profilegeneric(EVENT_SCALAR);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(EVENT_SCALAR, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}
bool ReadEventDataObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(EVENT_DATA_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(EVENT_DATA_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadDailyLoadScalar()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
  
    Load_ChoppedByteCount = read_profilegeneric(DL_SCALAR_DATA);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(DL_SCALAR_DATA, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadDailyLoadDataObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(DAILY_LOAD_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(DAILY_LOAD_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

bool ReadDailyLoadScalarObis()
{
  int load_res_count = 0;
  bool load_response = false;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = read_profilegeneric(DL_SCALAR_OBIS);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return ProfileFilecreate(DL_SCALAR_OBIS, Load_ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}

///////////////////////////////////////////////////////////////////////////////////////////////

bool ReadInstantScalarData()
{
  int load_res_count = 0;
  bool load_response = false;
  int ChoppedByteCount = 0;

  while(!load_response)
  {
    ChoppedByteCount = read_profilegeneric(INSTANTSCALAR);

    if(ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  if (ChoppedByteCount == 1) 
  {
    return ProfileFilecreate(INSTANTSCALAR,ChoppedByteCount, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear()); 
  }
  else
  {
    return false;
  }
}

int read_profilegeneric(int profiledata)
{
  //char LoadREQframeptr[30][MAX_SIZE] = {0};
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int local_i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  char MeterDataType = profiledata;

  bool frame_complete = false;
  int total_rowcount = 0;
  int dummy_rowcount = 0;
  int t_array_size = 0;
  int response_count = 0;

  bool Block_response = false;
  bool final_block = false;
   int segment_action = 0;
   int frame_size = 0;

  int mx_res_count = 0;

  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }

  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  if ((ResponseBuffer[arrindex][25] == 0x03 && ResponseBuffer[arrindex][26] == 0x02 && ResponseBuffer[arrindex][27] == 0x01 && ResponseBuffer[arrindex][28] == 0x00) ||
      (ResponseBuffer[arrindex][29] == 0x03 && ResponseBuffer[arrindex][30] == 0x02 && ResponseBuffer[arrindex][31] == 0x01 && ResponseBuffer[arrindex][32] == 0x00))
  {
//    CreateNoresponseDataFile("20", "METER INSTANT SUCCESS");
  }
  else
  {
//    CreateNoresponseDataFile("21", "METER INSTANT FAILURE");
    return 0;
  }

  GetSequenceNumber(0);

    //command frame starts 

    global_frame = "";
    special_counter = 0;
    response_count = 0;
    MeterCommandFrame(Fromdate, Todate, MeterDataType);

    // 04-04-2022
    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);

    ResByteCount = 0;

    if (MeterDataType == INSTANT_DATA)
    {
      instant_array[local_i] = arrindex;
    }
    else if (MeterDataType == BILLING_DATA)
    {
      billing_array[local_i] = arrindex;
    }

    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("TX : ");
      for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();

    }
    SerialRead(arrindex, ResByteCount);

    // BREAK METER READING OF NO RESPONSE FROM METER
    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }

    if(ResponseBuffer[arrindex][11] != 0xC4)
    {
      seriallogger_string("INVALID RESPONSE");
      return 0;
    }
    
    int temp_buff_size = 0;
//    if (ResponseBuffer[arrindex][1] == 0xA1)
//    {
//      temp_buff_size = 256;
//    }
//    else if (ResponseBuffer[arrindex][1] == 0xA2)
//    {
//      temp_buff_size = 512;
//    }
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

    for (int filedata = 0; filedata < (temp_buff_size + 2); filedata++)
    {
      global_frame = global_frame + String(ResponseBuffer[arrindex][filedata], HEX);
      global_frame = global_frame + " ";
    }
    global_frame.trim();
    if (ResponseBuffer[arrindex][11] == 0xC4)
    {
      if (ResponseBuffer[arrindex][12] == 0x02)
      {
        Block_response = true;
        
      }
      else if(ResponseBuffer[arrindex][12] == 0x01)
      {
        Block_response = false;

      }
    }


    segment_action = bitRead(ResponseBuffer[arrindex][1],3);

    if(METER_DEBUG == TRUE)
    {
      Serial2.println("Block_response " + String(Block_response));
      Serial2.println("segment_action " + String(segment_action));
    }
  
    if (Block_response == false && segment_action == 0)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 0 && ResponseBuffer[arrindex][14] == 0x01)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 1 && ResponseBuffer[arrindex][14] == 0x00)
    {
      frame_complete = true;
    }
    else
    {
      frame_complete = true;
    }

    /*****************************************************************************************/
    while (frame_complete) // first frame
    {
      if(mx_res_count >= COUNT_INST)
      {
          seriallogger_string("While count break : " +String(mx_res_count));
          break;
      }
        int check_A0_frame = bitRead(ResponseBuffer[arrindex][1],3);

        if (check_A0_frame == 0x00)
        {
          response_count++;
          FrameType = SPECIAL_FRAME;
        }
        else
        {
          FrameType = SUPERVISORY_FRAME;
        }


      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(++arrindex, LoadREQframeptr);

      ResByteCount = 0;

      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      if (METER_DEBUG == TRUE)
      {
        // Serial2.println();
        Serial2.print("SUPER TX : ");
        for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
        {
          Serial2.print(LoadREQframeptr[arrindex][i], HEX);
          Serial2.print(" ");
        }
        Serial2.println();

      }
      SerialRead(arrindex, ResByteCount);

      // BREAK METER READING OF NO RESPONSE FROM METER
      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");
        frame_complete = false;
        return 0;
      }

      global_frame = global_frame + "_";

      int temp_buff_size = 0;

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

      for (int c = 0; c < temp_buff_size + 2; c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }

      global_frame.trim();

      check_A0_frame = bitRead(ResponseBuffer[arrindex][1],3);
      
      if(Block_response == false)
      {
        if (check_A0_frame == 0x00)
        {
          frame_complete = false;
        }
      }
      else if(Block_response == true && final_block == false)
      {
        if (ResponseBuffer[arrindex][13] == 0xC1 && ResponseBuffer[arrindex][14] == 0x01)
        {
          if(check_A0_frame == 0x00)//A0
          {
            frame_complete = false;
          }
          else
          {
            final_block = true;
          }
        }
      }
      else if(final_block == true)
      {
        if (check_A0_frame == 0x00)
        {
          frame_complete = false;
        }
      }
      
      seriallogger_string("While count : "+String(mx_res_count));
      mx_res_count++;
    }
  

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();
  if (METER_DEBUG == TRUE)
  {
    // Serial2.println();
    Serial2.print("TX : ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
      Serial2.println();

  }
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;

  // CHOPPING LOAD REPONSES WILL BE DONE HERE
  // ChoppedByteCount = ChopLoadMeterResponse(ResponseBuffer, (arrindex + 1));
  // return ChoppedByteCount;
  return 1;
}

bool ReadBillingProfileEntry()
{
  bool load_response = false;
  int load_res_count = 0;
  int Billing_ChoppedByteCount = 0;

  while(!load_response)
  {
    int Billing_ChoppedByteCount = read_billentry(BILLING_DATA,BILLING_DATA,rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());

    if(Billing_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }
  return true;
}

bool ReadBillingProfileDataOnDemend()
{
  
   // for(int i = 0 ; i < availbillentry ;i++)
  // {
  bool load_response = false;
  int load_res_count = 0;
  int Billing_ChoppedByteCount = 0;
  
  int firstbillentry = ReadMSNFromFile("/firstentry.txt").toInt();
  int lastbillentry = ReadMSNFromFile("/lastentry.txt").toInt();
  readentrycount[0] = firstbillentry;
  readendcount[0] = lastbillentry;

  while(!load_response)
  {
    
    int Billing_ChoppedByteCount = read_profileforbill(BILLING_DATA,BILLING_DATA,rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());

    if(Billing_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  return true;
  
}

bool ReadBillingProfileData()
{
  
  // for(int i = 0 ; i < availbillentry ;i++)
  // {
  bool load_response = false;
  int load_res_count = 0;
  int Billing_ChoppedByteCount = 0;

  while(!load_response)
  {
    int count = ReadMSNFromFile("/availableentry").toInt();

    readentrycount[0] = count-1;
    readendcount[0]= count;
    int Billing_ChoppedByteCount = read_profileforbill(BILLING_DATA,BILLING_DATA,rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());

    if(Billing_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

  
  // }
  return true;
  
}





int read_profileforbill(int profiledata,char MType,int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year)
{
  
  //char LoadREQframeptr[30][MAX_SIZE] = {0};
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int local_i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  char MeterDataType = profiledata;

  bool frame_complete = false;
  // int total_rowcount = 0;
  // int dummy_rowcount = 0;
  // int t_array_size = 0;
  int response_count = 0;
  bool Block_response = false;
  bool final_block = false;

  int segment_action = 0;
  int frame_size = 0;
  int mx_res_count = 0;
///////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////
// MeterSerialNo_Final = "123989";
  char temp[5] = {0};
  String Load_Data_FIle_With_BlockID = "";
  String FinalLoad_str = "$";
  char temp_BlockID[5] = {0};
  sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
  FinalLoad_str += global_NodeID;
  FinalLoad_str += "_";
  FinalLoad_str += (String)meter_type;
  FinalLoad_str += "_";
  
  FinalLoad_str += "B";

  FinalLoad_str += "_";
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  FinalLoad_str += MeterSerialNo_Final;
  FinalLoad_str += "_";

  Load_Data_FIle_With_BlockID = "/BData"; // 13-04-2022
  
  Load_Data_FIle_With_BlockID += "/";

  sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)arg_month);
  Load_Data_FIle_With_BlockID += temp;
  // sprintf(temp, "%04s", (String)arg_year);
  // Load_Data_FIle_With_BlockID += temp;
  Load_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)g_hours);
  Load_Data_FIle_With_BlockID += temp;

  // if (METER_MAKE == LT)
  sprintf(temp, "%02s", (String)arg_minute);
  // else
  //   sprintf(temp, "%02s", (String)rtc.getMinute());

  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  Load_Data_FIle_With_BlockID += "B.txt";  

  
  seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
  FinalLoad_str.trim();
  WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, "{\"data2\":\"");
  appendFile_new(LittleFS,Load_Data_FIle_With_BlockID, FinalLoad_str);
 
/////////////////////////////////////////////////////////////////////////////////////////////////    

  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }


  if ((ResponseBuffer[arrindex][25] == 0x03 && ResponseBuffer[arrindex][26] == 0x02 && ResponseBuffer[arrindex][27] == 0x01 && ResponseBuffer[arrindex][28] == 0x00) ||
      (ResponseBuffer[arrindex][29] == 0x03 && ResponseBuffer[arrindex][30] == 0x02 && ResponseBuffer[arrindex][31] == 0x01 && ResponseBuffer[arrindex][32] == 0x00))
  {
//    CreateNoresponseDataFile("20", "METER INSTANT SUCCESS");
  }
  else
  {
//    CreateNoresponseDataFile("21", "METER INSTANT FAILURE");
    return 0;
  }

    GetSequenceNumber(0);

    global_frame = "";
    special_counter = 0;
    response_count = 0;
    MeterCommandFrame(Fromdate, Todate, MeterDataType);
    // 04-04-2022
    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);

    ResByteCount = 0;

    if (MeterDataType == INSTANT_DATA)
    {
      instant_array[local_i] = arrindex;
    }
    else if (MeterDataType == BILLING_DATA)
    {
      billing_array[local_i] = arrindex;
    }

    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("TX : ");
      for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();

    }
    SerialRead(arrindex, ResByteCount);
    
    int temp_buff_size = 0;
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("RX : ");
      for (int temp_i = 0; temp_i < temp_buff_size + 2; temp_i++)
      {
        Serial2.print(ResponseBuffer[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
    }

    // BREAK METER READING OF NO RESPONSE FROM METER
    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }

    temp_buff_size = 0;
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);
    //Serial2.print("temp_buff_size" + String(temp_buff_size));

    for (int filedata = 0; filedata < (temp_buff_size + 2); filedata++)
    {
      global_frame = global_frame + String(ResponseBuffer[arrindex][filedata], HEX);
      global_frame = global_frame + " ";
    }
    global_frame.trim();

    appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,global_frame);

    if (ResponseBuffer[arrindex][11] == 0xC4)
    {
      if (ResponseBuffer[arrindex][12] == 0x02)
      {
        Block_response = true;
      }
       else if(ResponseBuffer[arrindex][12] == 0x01)
      {
        Block_response = false;
      }
    }



    segment_action = bitRead(ResponseBuffer[arrindex][1],3);
    
    if (Block_response == false && segment_action == 0)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 0 && ResponseBuffer[arrindex][14] == 0x01)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 1 && ResponseBuffer[arrindex][14] == 0x00)
    {
      frame_complete = true;
    }
    else
    {
      frame_complete = true;
    }

    /*****************************************************************************************/
    while (frame_complete) // first frame
    {
      if(mx_res_count >= COUNT_BILL)
      {
          seriallogger_string("While count break : " +String(mx_res_count));
          break;
      }
        segment_action = bitRead(ResponseBuffer[arrindex][1],3);

        if (segment_action == 0x00) //A0
        {
          response_count++;
          FrameType = SPECIAL_FRAME;
        }
        else
        {
          FrameType = SUPERVISORY_FRAME;
        }
      
      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(arrindex, LoadREQframeptr);

      ResByteCount = 0;

      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      if (METER_DEBUG == TRUE)
      {
        // Serial2.println();
        Serial2.print("SUPER TX : ");
        for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
        {
          Serial2.print(LoadREQframeptr[arrindex][i], HEX);
          Serial2.print(" ");
        }
       Serial2.println();

      }

      SerialRead(arrindex, ResByteCount);

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

      if (METER_DEBUG == TRUE)
      {
        Serial2.println();
        // Serial2.print("temp_buff_size " + String(temp_buff_size));
        Serial2.print("RX : ");
        for (int temp_i = 0; temp_i < temp_buff_size + 2; temp_i++)
        {
          Serial2.print(ResponseBuffer[arrindex][temp_i], HEX);
          Serial2.print(" ");
        }
      }

      // BREAK METER READING OF NO RESPONSE FROM METER
      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");
        frame_complete = false;
        return 0;
      }
//      global_frame = "";
      global_frame = "_";

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);
      Serial2.print("temp_buff_size" + String(temp_buff_size));

      for (int c = 0; c < temp_buff_size + 2; c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }

      global_frame.trim();
      

      appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,global_frame);

      segment_action = bitRead(ResponseBuffer[arrindex][1],3);

      if(Block_response == false)
      {
        if (segment_action == 0x00)
        {
          frame_complete = false;
        }
      }
      else if(Block_response == true && final_block == false)
      {
        if (ResponseBuffer[arrindex][13] == 0xC1 && ResponseBuffer[arrindex][14] == 0x01)
        {
          if(segment_action == 0x00)
          {
            frame_complete = false;
          }
          else
          {
            final_block = true;
          }
        }
      }
      else if(final_block == true)
      {
        if (segment_action == 0x00)
        {
          frame_complete = false;
        }
      }

      seriallogger_string("While count : "+String(mx_res_count));
      mx_res_count++;
    }
    
  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();
  if (METER_DEBUG == TRUE)
  {
    // Serial2.println();
    Serial2.print("TX : ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
      Serial2.println();

  }
  
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;


/////////////////////////////////////////////////////////////////////////////////////////

  appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,"$");
  appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,"\",\"gwid\":\"" + GWID + "\"}");
  String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);
  // readFile(LittleFS,Load_Data_FIle_With_BlockID);
   seriallogger_string("billing data " + String(temp_load_data_string_for_validation).length());
  
  
  if (temp_load_data_string_for_validation.startsWith("{"))
  {
    temp_load_data_string_for_validation.trim();
    if (temp_load_data_string_for_validation.endsWith("}"))
    {
           return 1 ;
    }
    else
    {
      LittleFS.remove(Load_Data_FIle_With_BlockID);
      return 0;
    }
  }
  else
  {
    LittleFS.remove(Load_Data_FIle_With_BlockID);
    return 0;
  }


  return 1 ;
}

// bool CreateInstantDataFile(int obis_array, int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year) // added arg_month on 16-06-2022 //added arg_year on 18-06-2022
// {
//   // MeterSerialNo_Final = "123989";
//   char temp[5] = {0};
//   String Load_Data_FIle_With_BlockID = "";
//   String FinalLoad_str = "$";
//   char temp_BlockID[5] = {0};
//   sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
//   FinalLoad_str += global_NodeID;
//   FinalLoad_str += "_";
//   FinalLoad_str += (String)meter_type;
//   FinalLoad_str += "_";
//   if (obis_array == 3)
//   {
//     FinalLoad_str += "IP";
//   }
//   else if (obis_array == 2)
//   {
//     FinalLoad_str += "IPO";
//   }
//   else if (obis_array == 1)
//   {
//     FinalLoad_str += "IPSV";
//   }
//   else if (obis_array == 0)
//   {
//     FinalLoad_str += "IPSO";
//   }
//   FinalLoad_str += "_";
//   FinalLoad_str += temp_BlockID;
//   FinalLoad_str += "_";
//   sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
//   FinalLoad_str += temp_BlockID;
//   FinalLoad_str += "_";
//   FinalLoad_str += MeterSerialNo_Final;
//   FinalLoad_str += "_";

//   int frame_count = instant_array[obis_array];
//   int Loop_stop_flag = 0;
//   int extended_frame_size = 0;

//   FinalLoad_str += global_frame;

//   FinalLoad_str.trim();
//   FinalLoad_str += "$";

//   Load_Data_FIle_With_BlockID = "/OBSC"; // 13-04-2022
//   Load_Data_FIle_With_BlockID += "/";

//   sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
//   Load_Data_FIle_With_BlockID += temp;

//   Load_Data_FIle_With_BlockID += "_";

//  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
//  Load_Data_FIle_With_BlockID += temp;
//  sprintf(temp, "%02s", (String)arg_month);
//  Load_Data_FIle_With_BlockID += temp;
// //  sprintf(temp, "%04s", (String)arg_year);
// //  Load_Data_FIle_With_BlockID += temp;
//  Load_Data_FIle_With_BlockID += "_";
//   sprintf(temp, "%02s", (String)g_hours);
//   Load_Data_FIle_With_BlockID += temp;

//   // if (METER_MAKE == LT)
//   sprintf(temp, "%02s", (String)arg_minute);
//   // else
//   //   sprintf(temp, "%02s", (String)rtc.getMinute());

//   Load_Data_FIle_With_BlockID += temp;

//   Load_Data_FIle_With_BlockID += "_";

//   if (obis_array == 3)
//   {
//     Load_Data_FIle_With_BlockID += "IP.txt";
//   }
//   else if (obis_array == 2)
//   {
//     Load_Data_FIle_With_BlockID += "IPO.txt";
//   }
//   else if (obis_array == 1)
//   {
//     Load_Data_FIle_With_BlockID += "IPSV.txt";
//   }
//   else if (obis_array == 0)
//   {
//     Load_Data_FIle_With_BlockID += "IPSO.txt";
//   }

//   seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
//   // seriallogger_string("Load DATA: " + FinalLoad_str);
//   //  seriallogger_string(Load_Data_FIle_With_BlockID);
//   //  seriallogger_string("\r\n");
//   WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);
//   // ReadFromFile(Load_Data_FIle_With_BlockID);

//   // Version 3
//   // Code to validate whether data has been written into file properly
//   String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);
 
  
//   readFile(LittleFS,Load_Data_FIle_With_BlockID);
  
//   if (temp_load_data_string_for_validation.startsWith("$"))
//   {
//     temp_load_data_string_for_validation.trim();
//     if (temp_load_data_string_for_validation.endsWith("$"))
//       return true;
//     else
//     {
//       LittleFS.remove(Load_Data_FIle_With_BlockID);
//       return false;
//     }
//   }
//   else
//   {
//     LittleFS.remove(Load_Data_FIle_With_BlockID);
//     return false;
//   }
// }

int read_billentry(int profiledata,char MType,int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year)
{
  
  //char LoadREQframeptr[30][MAX_SIZE] = {0};
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int local_i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  char MeterDataType = profiledata;

  bool frame_complete = false;
  // int total_rowcount = 0;
  // int dummy_rowcount = 0;
  // int t_array_size = 0;
  int response_count = 0;
  bool Block_response = false;
  bool final_block = false;

  int segment_action = 0;
  int frame_size = 0;
  int mx_res_count = 0;
///////////////////////////////////////////////////////////////////////////////////////////////////////////

/////////////////////////////////////////////////////////////////////////////////////////////////    

  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  if ((ResponseBuffer[arrindex][25] == 0x03 && ResponseBuffer[arrindex][26] == 0x02 && ResponseBuffer[arrindex][27] == 0x01 && ResponseBuffer[arrindex][28] == 0x00) ||
      (ResponseBuffer[arrindex][29] == 0x03 && ResponseBuffer[arrindex][30] == 0x02 && ResponseBuffer[arrindex][31] == 0x01 && ResponseBuffer[arrindex][32] == 0x00))
  {
//    CreateNoresponseDataFile("20", "METER INSTANT SUCCESS");
  }
  else
  {
//    CreateNoresponseDataFile("21", "METER INSTANT FAILURE");
    return 0;
  }

  GetSequenceNumber(0);


    global_frame = "";
    special_counter = 0;
    response_count = 0;
    MeterCommandFrame(Fromdate, Todate, MeterDataType);
    // 04-04-2022
    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);

    ResByteCount = 0;

    if (MeterDataType == INSTANT_DATA)
    {
      instant_array[local_i] = arrindex;
    }
    else if (MeterDataType == BILLING_DATA)
    {
      billing_array[local_i] = arrindex;
    }

    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("TX : ");
      for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();

    }
    SerialRead(arrindex, ResByteCount);
    
    int temp_buff_size = 0;
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("RX : ");
      for (int temp_i = 0; temp_i < temp_buff_size + 2; temp_i++)
      {
        Serial2.print(ResponseBuffer[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
    }

    // BREAK METER READING OF NO RESPONSE FROM METER
    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }

      availbillentry = (ResponseBuffer[arrindex][19]);
      bavailflag = 0;

     if (availbillentry < 27 && availbillentry > 0)
     {
        WritePostDataIntoBlockIDFile("/availableentry", String(availbillentry));
     }
     else
     {
        return 0;
     }
    seriallogger_string("THE BILLING ENTRIES ARE : " +String(availbillentry));
    

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();
  if (METER_DEBUG == TRUE)
  {
    // Serial2.println();
    Serial2.print("TX : ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
      Serial2.println();

  }
  
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;


/////////////////////////////////////////////////////////////////////////////////////////

  return 1 ;
}

bool CreateBillingDataFile(int obis_array, int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year) // added arg_month on 16-06-2022 //added arg_year on 18-06-2022
{
  // MeterSerialNo_Final = "123989";
  char temp[5] = {0};
  String Load_Data_FIle_With_BlockID = "";
  String FinalLoad_str = "$";
  char temp_BlockID[5] = {0};
  sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
  FinalLoad_str += global_NodeID;
  FinalLoad_str += "_";
  FinalLoad_str += (String)meter_type;
  FinalLoad_str += "_";
  if (obis_array == 3)
  {
    FinalLoad_str += "B";
  }
  else if (obis_array == 2)
  {
    FinalLoad_str += "BO";
  }
  else if (obis_array == 1)
  {
    FinalLoad_str += "BSV";
  }
  else if (obis_array == 0)
  {
    FinalLoad_str += "BSO";
  }

  FinalLoad_str += "_";
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  FinalLoad_str += MeterSerialNo_Final;
  FinalLoad_str += "_";

  int frame_count = billing_array[obis_array];
  int Loop_stop_flag = 0;
  int extended_frame_size = 0;

  FinalLoad_str = global_frame;

  FinalLoad_str.trim();
  FinalLoad_str += "$";

  Load_Data_FIle_With_BlockID = "/OBSC"; // 13-04-2022
  Load_Data_FIle_With_BlockID += "/";

  sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)arg_month);
  Load_Data_FIle_With_BlockID += temp;
  // sprintf(temp, "%04s", (String)arg_year);
  // Load_Data_FIle_With_BlockID += temp;
  Load_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)g_hours);
  Load_Data_FIle_With_BlockID += temp;

  // if (METER_MAKE == LT)
  sprintf(temp, "%02s", (String)arg_minute);
  // else
  //   sprintf(temp, "%02s", (String)rtc.getMinute());

  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  if (obis_array == 3)
  {
    Load_Data_FIle_With_BlockID += "B.txt";
  }
  else if (obis_array == 2)
  {
    Load_Data_FIle_With_BlockID += "BO.txt";
  }
  else if (obis_array == 1)
  {
    Load_Data_FIle_With_BlockID += "BSV.txt";
  }
  else if (obis_array == 0)
  {
    Load_Data_FIle_With_BlockID += "BSO.txt";
  }

  seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
  // seriallogger_string("Load DATA: " + FinalLoad_str);

  WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);

  // Code to validate whether data has been written into file properly
  String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);

  if (temp_load_data_string_for_validation.startsWith("$"))
  {
    temp_load_data_string_for_validation.trim();
    if (temp_load_data_string_for_validation.endsWith("$"))
      return true;
    else
    {
      LittleFS.remove(Load_Data_FIle_With_BlockID);
      return false;
    }
  }
  else
  {
    LittleFS.remove(Load_Data_FIle_With_BlockID);
    return false;
  }
}

// bool CreateBillingScalarFile(int obis_array, int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year) // added arg_month on 16-06-2022 //added arg_year on 18-06-2022
// {
//   // MeterSerialNo_Final = "123989";
//   char temp[5] = {0};
//   String Load_Data_FIle_With_BlockID = "";
//   String FinalLoad_str = "$";
//   char temp_BlockID[5] = {0};
//   sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
//   FinalLoad_str += global_NodeID;
//   FinalLoad_str += "_";
//   FinalLoad_str += (String)meter_type;
//   FinalLoad_str += "_";
//   FinalLoad_str += "BSV";
//   FinalLoad_str += "_";
//   FinalLoad_str += temp_BlockID;
//   FinalLoad_str += "_";
//   sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
//   FinalLoad_str += temp_BlockID;
//   FinalLoad_str += "_";
//   FinalLoad_str += MeterSerialNo_Final;
//   FinalLoad_str += "_";

//   int frame_count = billing_array[obis_array];
//   int Loop_stop_flag = 0;
//   int extended_frame_size = 0;

//   FinalLoad_str = global_frame;

//   FinalLoad_str.trim();
//   FinalLoad_str += "$";

//   Load_Data_FIle_With_BlockID = "/OBSC"; // 13-04-2022
//   Load_Data_FIle_With_BlockID += "/";

//   sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
//   Load_Data_FIle_With_BlockID += temp;

//   Load_Data_FIle_With_BlockID += "_";

//   sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
//   Load_Data_FIle_With_BlockID += temp;
//   sprintf(temp, "%02s", (String)arg_month);
//   Load_Data_FIle_With_BlockID += temp;
//   // sprintf(temp, "%04s", (String)arg_year);
//   // Load_Data_FIle_With_BlockID += temp;
//   Load_Data_FIle_With_BlockID += "_";
//   sprintf(temp, "%02s", (String)g_hours);
//   Load_Data_FIle_With_BlockID += temp;

//   // if (METER_MAKE == LT)
//   sprintf(temp, "%02s", (String)arg_minute);
//   // else
//   //   sprintf(temp, "%02s", (String)rtc.getMinute());

//   Load_Data_FIle_With_BlockID += temp;

//   Load_Data_FIle_With_BlockID += "_";

//   Load_Data_FIle_With_BlockID += "BSV.txt";

//   seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
//   // seriallogger_string("Load DATA: " + FinalLoad_str);

//   WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);

//   // Code to validate whether data has been written into file properly
//   String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);

//   if (temp_load_data_string_for_validation.startsWith("$"))
//   {
//     temp_load_data_string_for_validation.trim();
//     if (temp_load_data_string_for_validation.endsWith("$"))
//       return true;
//     else
//     {
//       LittleFS.remove(Load_Data_FIle_With_BlockID);
//       return false;
//     }
//   }
//   else
//   {
//     LittleFS.remove(Load_Data_FIle_With_BlockID);
//     return false;
//   }
// }

void setup()
{
  pinMode(DATA_COMMUNICATION, OUTPUT);
  pinMode(FOURG_COMMUNICATION, OUTPUT);
  pinMode(RS232_INDICATOR,OUTPUT);

  if (debug_flag != TRUE)
  {
    Serial.begin(9600);
  }


  if (METER_DEBUG == TRUE)
  {
    Serial2.begin(115200);
    Serial.begin(9600);
  }
  
  digitalWrite(RS232_INDICATOR, LOW);

  pinMode(MODULE_RESET_4G, OUTPUT);
  pinMode(MODULE_RESET_ESP, OUTPUT);
  esp_task_wdt_init(WDT_TIMEOUT, true); // enable panic so ESP32 restarts
  esp_task_wdt_add(NULL);         // add current thread to WDT watch
  
  /*****************************************/
  if (!LittleFS.begin(LITTLEFS_MOUNT))
  {
    seriallogger_string("LittleFS Mount Failed");
    return;
  }
   if (debug_flag == 1)
  {
    Serial.begin(115200);
    Serial.flush();
  }

  Serial2.begin(115200);
  Serial2.flush();
  Serial2.setRxBufferSize(RX_BUFFER_MAX);

  String node_details = node_serialization(buildid);
  Serial.println("node_details: " + node_details);
  node_details = "NSGW700080,NSTG700080,12345678";
  if(node_details == "0")
  {
    node_details = "";
    basicATcommands();
    node_details = node_serialization_4G(buildid);
  }

  if(node_details.indexOf("NSTG")>=0)
  {
    
    String temp_gwid = node_details.substring(0, 10);
    String node_ssid = node_details.substring(11, 21);
    password_aes = node_details.substring(22);
    temp_gwid.trim();
    node_ssid.trim();
    password_aes.trim();
    GWID = temp_gwid;
    global_NodeID = node_ssid;

    Serial.println("4G NODE : "+ GWID +" SOFTWARE FIRMWARE VERSION: " + String(gw_current_firmware_version));
    Serial.println("Node ID: " + global_NodeID);
    Serial.println("Gateway ID: " + GWID);
  }
  else
  {
     ESP.restart();
  }

  read_meter_Data();
  esp_task_wdt_reset();

  // testingRS232();

  if (debug_flag != TRUE)
  {
    readonetime();
    esp_task_wdt_reset();
  }
 
  
  
  gsm_init(); 
  esp_task_wdt_reset(); 



  if (METER_DEBUG != TRUE)
  {
    modem_start();
    esp_task_wdt_reset();
  }

  // read_meter_Data();
  // esp_task_wdt_reset();

}

void loop()
{
  // put your main code here, to run repeatedly:
  digitalWrite(DATA_COMMUNICATION, HIGH);
  delay(1000);
  digitalWrite(DATA_COMMUNICATION, LOW);
  if(METER_DEBUG == TRUE)
  {
    Serial2.println(rtc.getMinute(),HEX);
  }
  
  // if (resume_reading_gsm == 1)//&& is_reading_interrupted == 1)
  //if ((rtc.getMinute() % 5 == 0))
  // if (((rtc.getMinute() == 0 || rtc.getMinute() == 20 || rtc.getMinute() == 40)))
  // {
    
    read_meter_Data();
    esp_task_wdt_reset();
    
    hardReset();
  // }

  delay(1000);
  ////////////////////////////////////////////////////
}

void gsm_init()
{
  SERIAL_MST("Waiting for 30 seconds");
  delay(30000);
  Serial2.flush();
  Serial2.setRxBufferSize(RX_BUFFER_MAX);
  SERIAL_MST("********************4G NODE : "+ GWID +"  VERSION : " + String(gw_current_firmware_version) + "********************");
  SERIAL_MST("TOTAL AVAILABLE MEMORY : " +String(LittleFS.totalBytes() - LittleFS.usedBytes()));

  SERIAL_MST("Deleting filenameslist file");
  deleteFile(LittleFS, "/filenameslist");
  SERIAL_MST("Deleting prev gw OTA file");
  deleteFile(LittleFS, "/download.bin");
  if (LittleFS.usedBytes() > 1000000)
  {
    SERIAL_MST("GATEWAY IS FULL");
  }
  else
  {
    SERIAL_MST("Sufficient memory available in gateway");
  }
  // SERIAL_MST("Waiting 5 seconds\n");
  // delay(10000);
  // Code for WiFi based OTA

  
  int wifidownload_status = 0;

  wifidownload_status = WiFi_downloadFile();
  if (wifidownload_status == 1)
  {
    SERIAL_MST("INIT WIFI OTA");
    handleupdatefirmwareWIFI();
  }

  String otaStatus = "";
  otaStatus = readFile(LittleFS, "/gwotastatus");
  if (otaStatus.indexOf("1111") >= 0)
  {
    writeFile("/gwotastatus", "0000");
    handleupdatefirmware();
  }
  else
  {
    // deleteFile(LittleFS, "/download.bin");
    deleteFile(LittleFS, "/gwotadownload.bin");
    writeFile("/gwotastatus", "0000");
    readFile(LittleFS, "/gwotastatus");
  }
  SERIAL_MST("SDK version : " + String(ESP.getSdkVersion()));
 
  // rtc.setTime(55, 04, 12, 29, 04, 2022); // 29th Apr 2022 12:04:55
  rtc.setTime(00,00, 06, 15, 11, 2022); // 15th Nov 2022 12:04:59
  int statusofdir = checkforDirectory("/meterreading", 3);
  if (statusofdir == 0)
  {
    createDir(LittleFS, "/meterreading");
  }
  int filesize_indicator = 0;
  filesize_indicator = checkforFiles(LittleFS, "/meterreading", 3,"/filenamecount");

  if (filesize_indicator)
  {
    writeFile("/meterreading" + g_filename + String(fileCount), "");
    writeFile("/filenamecount", String(fileCount));
  }

  statusofdir = checkforDirectory("/IPLreading", 3);
  if (statusofdir == 0)
  {
    createDir(LittleFS, "/IPLreading");
  }
   filesize_indicator = 0;
  filesize_indicator = checkforFiles(LittleFS, "/IPLreading", 3,"/IPLcount");

  if (filesize_indicator)
  {
    writeFile("/IPLreading" + g_filename + String(fileCount), "");
    writeFile("/IPLcount", String(fileCount));
  }
  
  SERIAL_MST("Deleting any previous commands if present");
  delete_commands("/commands");
  createDir(LittleFS, "/commands");
  ////////////////////////////////////////////////////////////
}

void read_meter_Data()
{
  String Check_Billing_Status = "";
  String Check_Scalar_Status = "";
  String Check_Event_Status = "";
  String Check_OBIS_Status = "";
  String Check_Insta_Status = "";
  String Check_BillingOnDemand_Status = "";
  String Check_OneFullDayLoad_Status = "";

  // String node_details = node_serialization(4);

  // String temp_gwid = node_details.substring(0,10);
  // String node_ssid = node_details.substring(11,21);
  // String password_aes = node_details.substring(22);
  // temp_gwid.trim();
  // node_ssid.trim();
  // password_aes.trim();
  // GWID = temp_gwid;
  // global_NodeID = node_ssid;

  // pinMode(RELAY_ON, OUTPUT);
  // pinMode(RELAY_OFF, OUTPUT);

  if (checkforDirectory("/NodeID", 3) == 0)
  {
    createDir(LittleFS, "/NodeID");
  }

  if (checkforDirectory("/CommandDirectory", 3) == 0)
  {
    createDir(LittleFS, "/CommandDirectory");
  }

  if (checkforDirectory("/RelayStatus", 3) == 0)
  {
    createDir(LittleFS, "/RelayStatus");
  }

  if (checkforDirectory("/StatusFlag", 3) == 0)
  {
    createDir(LittleFS, "/StatusFlag");
  }

  if (checkforDirectory("/BData", 3) == 0)
  {
    createDir(LittleFS, "/BData");
  }

  if (checkforDirectory("/blkstatus", 3) == 0)
  {
    createDir(LittleFS, "/blkstatus");
  }

  if (checkforDirectory("/OBSC", 3) == 0)
  {
    createDir(LittleFS, "/OBSC");
  }

    if (checkforDirectory("/IPL", 3) == 0)
  {
    createDir(LittleFS, "/IPL");
  }

  if (checkforDirectory("/MeterSlNo", 3) == 0)
  {
    createDir(LittleFS, "/MeterSlNo");
  }

  seriallogger_string("SOFTWARE FIRMWARE VERSION: " + String(gw_current_firmware_version));

  // Serial.println("SOFTWARE FIRMWARE VERSION: " + (String)SOFTWARE_VERSION);
  // Serial.println("Node ID: " + global_NodeID);
  // Serial.println("Gateway ID: " + GWID);
  // String node_details = node_serialization(buildid);

  // String ssid_node = node_details.substring(0,10);
  //  String ssid_node = node_details.substring(11,20);

  // global_NodeID = ssid_node;

  // seriallogger_string("Node ID: " + global_NodeID);

  // global_NodeID.trim();

  // int n = global_NodeID.length();
  // char temp_global_NodeID[n + 1] = {0};
  // strcpy(temp_global_NodeID, global_NodeID.c_str());

  // String password_aes = node_details.substring(11, 35);//password_generator(temp_global_NodeID);

  // TEST
  // global_NodeID = "NSTG002630";//2501
  // String password_aes = "";
  seriallogger_string("Node ID: " + global_NodeID);

  
  CheckLogFileSize();

  delay(2000);
  seriallogger_string("****************START*****************");

  if (METER_DEBUG == TRUE)
  {
    Serial2.println("Wait for 60 Sec");
  }
  
  delay(60000);
  //send_disconnect_command_to_serial();

  int meter_index = 0;
  SERIAL_MST("Gateway time set as : " + String(rtc.getTime("%A, %B %d %Y %H:%M:%S")));
  int temptime =  rtc.getDay(); 
  int get_hour = rtc.getTime("%H").toInt();  
  String todaytime = "";
  todaytime = ReadMSNFromFile("/readdate.txt");
  todaytime.trim();
  String(temptime).trim();
  String(get_hour).trim();

  
//  SERIAL_MST("****************today time*****************  " +todaytime);
//  SERIAL_MST("****************temp time*****************  " +String(temptime));
//  SERIAL_MST("****************gethour*****************  " + String(get_hour));

  if((todaytime != String(temptime)) && (get_hour >= 8) && todaytime != "NILL" && todaytime != "")
  {
//       SERIAL_MST("******IM IN ***********  " );
       WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt","1");
       WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt","1");
       WritePostDataIntoBlockIDFile("/StatusFlag/OBIS.txt","1");
       WritePostDataIntoBlockIDFile("/readdate.txt",String(temptime));
  }

  //AutoDetectMeterType(meter_index);
  // int dummy_index = 0;
  int dummy_count = 0;
  int retvalue = 0;
  while (meter_index < TOTAL_NO_OF_KEYS)
  {
    
    retvalue = AutoDetectMeterType(meter_index);
    if (retvalue == 1)
    { 
      break;
    }

    if(dummy_count > 2 || retvalue == 2)
    {
      meter_index++;
      dummy_count = 0;
    }
    else
    {
      dummy_count++;
    }
    
  }

  seriallogger_string("meter_index: " + (String)meter_index);

  if ((METER_MAKE < TOTAL_NO_OF_KEYS) && meter_index < TOTAL_NO_OF_KEYS)
  {
    // delay(10000);

    int status_of_time = 0;
    int date_time_count = 0;
    bool date_time = false ;

    while(!date_time)
    {
      status_of_time = InitialiseESP32RTC();

      if(status_of_time == 1 || date_time_count > 2)
      {
        date_time = true;
      }
      else
      {
        date_time_count++;
      }
    }
    
    if (status_of_time == 1)
    {
      // NEW FS

      String BlockIDsFileName = ""; // 19-04-2022
      BlockIDsFileName = "/blkstatus";
      BlockIDsFileName += "/";
      BlockIDsFileName += (String)g_day; //(String)rtc.getDay();
      BlockIDsFileName += "-";
      BlockIDsFileName += (String)g_month /*(rtc.getMonth()+1)*/;
      BlockIDsFileName += "-";
      BlockIDsFileName += (String)g_year /*rtc.getYear()*/;
      BlockIDsFileName += ".txt";

      seriallogger_string(BlockIDsFileName);

      if (g_year > 2022)
      {
        CreateBlockIDFIle(BlockIDsFileName); // 19-04-2022
      }

      // MeterSerialNo_Final = "";
      // MeterSerialNo_Final = ReadMSNFromFile("/MeterSlNo/MSN.txt");
      // MeterSerialNo_Final.trim();
        int serialno_true = 0;
        int sno_retry_count = 0;

        while(!serialno_true)
        {
          ReadMeterDetails();
          if(MeterSerialNo_Final == "" || MeterSerialNo_Final == "NILL" || (sno_retry_count > 4))
          {
            serialno_true = 0;
          }
          else
          {
            serialno_true = 1;
            sno_retry_count++;
          }
        }
       //////////////////////////////////
       readdailyload();
       ReadDailyLoadDataObis();
       ReadDailyLoadScalar();
       ReadDailyLoadScalarObis();
       /////////////////////////////////
      //  ReadMissingLoadProfileBlock();
      //  ReadInstantProfileData();
      //  ReadBillingProfileEntry();
        // readblockload();


//////////////////////////////////////////////////////////////////////////


      Check_Billing_Status = ReadMSNFromFile("/StatusFlag/Bill.txt");
      Check_Billing_Status.trim();
      Check_Scalar_Status = ReadMSNFromFile("/StatusFlag/Scalar.txt");
      Check_Scalar_Status.trim();
      Check_Event_Status = ReadMSNFromFile("/StatusFlag/Event.txt");
      Check_Event_Status.trim();
      Check_OBIS_Status = ReadMSNFromFile("/StatusFlag/OBIS.txt");
      Check_OBIS_Status.trim();
      Check_Insta_Status = ReadMSNFromFile("/StatusFlag/Instant.txt");
      Check_Insta_Status.trim();
      Check_BillingOnDemand_Status = ReadMSNFromFile("/StatusFlag/BillOnDemand.txt");
      Check_BillingOnDemand_Status.trim();
      Check_OneFullDayLoad_Status = ReadMSNFromFile("/StatusFlag/Load.txt");
      Check_OneFullDayLoad_Status.trim();

      if(METER_DEBUG == TRUE)
      {
        Serial2.print("Bill " + Check_Billing_Status);
        Serial2.print("Scalar " + Check_Scalar_Status);
        Serial2.print("Event " + Check_Event_Status);
        Serial2.print("OBIS " + Check_OBIS_Status);
        Serial2.print("Insta " + Check_Insta_Status);
        Serial2.print("Bill On Demand " +Check_BillingOnDemand_Status);
      }

      if(Check_Billing_Status == "1")
      {
        ReadBillingProfileData();
        WritePostDataIntoBlockIDFile("/StatusFlag/Bill.txt","0");
      }

      if (Check_Scalar_Status == "1")
      {
        ReadInstantScalarData();
        ReadBillingScalarData();
        ReadLoadProfileScalar();
        ReadEventScalar();
        WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt","0");
      }

      if (Check_Event_Status == "1")
      {
        ReadEventProfileData(EVENTVOLTAGE);
        ReadEventProfileData(EVENTCURRENT);
        ReadEventProfileData(EVENTPOWER);
        ReadEventProfileData(EVENTTRANSACTION);
        ReadEventProfileData(EVENTOTHER);
        ReadEventProfileData(EVENTNONROLL);
        WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt","0");
      }

      if (Check_OBIS_Status == "1")
      {
        ReadLoadDataObis();
        ReadLoadScalarObis();
        ReadInstaDataObis();
        ReadInstaScalarObis();
        ReadBillingDataObis();
        ReadBillingScalarObis();
        ReadEventScalarObis();
        ReadEventDataObis();
        WritePostDataIntoBlockIDFile("/StatusFlag/OBIS.txt","0");
      }

      if (Check_Insta_Status == "1")
      {
        ReadInstantProfileData();
        WritePostDataIntoBlockIDFile("/StatusFlag/Instant.txt","0");
      }

      if(Check_BillingOnDemand_Status == "1")
      {
        ReadBillingProfileDataOnDemend();
        WritePostDataIntoBlockIDFile("/StatusFlag/BillOnDemand.txt","0");
      }
      
      if(Check_OneFullDayLoad_Status == "1")
      {
        readblockload();
        WritePostDataIntoBlockIDFile("/StatusFlag/Load.txt","0");
      }
      
      CheckBlockStatusFilesSize();
      delay(2000);
    }
    else
    {
      CYCLE_TIME_IN_MINS = 1;
      seriallogger_string("DATE TIME SYNC FAILED");
      seriallogger_string("****************END*****************");
      CreateNoresponseDataFile("04", "DATE TIME SYNC FAILED");
    }
  }
  else
  {
    CYCLE_TIME_IN_MINS = 1;
    seriallogger_string("METER MAKE DETECTION FAILED");
    seriallogger_string("****************END*****************");
    CreateNoresponseDataFile("02", "METER MAKE DETECTION FAILED");
  }
  
  delay(500);
}

void modem_start()
{
  Serial2.setRxBufferSize(RX_BUFFER_MAX);
  SERIAL_MST("********************START********************");
  SERIAL_MST("MEMORY DETAILS : " + String(ESP.getFreeHeap()));
  if (cfc == 25000)
  {
    SERIAL_MST("CFC counter full!!");
    cfc = 0;
  }
  
  
  LocalNetworkReader();
  esp_task_wdt_reset();

  internetDataSender();
  esp_task_wdt_reset();

  
  if (debug_flag == 1)
  {
    Serial.flush();
  }
  Serial2.flush();
  SERIAL_MST("********************END********************");

  getAndExecuteCommands();
  esp_task_wdt_reset();

  if (module_reset_count == 250)
  {
    SERIAL_MST("Module reset count reached 250!");
    hardReset();
  }
}

int SNRMframing() // bhavya added on 03-12-2021
{
  char FrameType = SNRM_FRAME;
  HdlcWrapperEncoding(FrameType, 0, 0);
  return 0;
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
  length++;     // 1
  char serveraddress = 0x03;

  length++; // 2
  char Clientaddress = 0x41;

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

  FrameFormat_length[0] = 0xA0;   // HDLC_FRAME_FORMAT_WITHOUT_SEGMENTATION;
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
    cFrameType = (char)((g_RRR << 5) | 0x10);   // Receive Sequence
    cFrameType = (char)(cFrameType | (g_SSS << 1)); // Send Seqence
    break;
  case 3:
    cFrameType = (char)((g_RRR << 5) | 0x10); // Receive Sequence
    cFrameType = (char)(cFrameType | 0x01);   // Send Seqence
    break;
  }
  return cFrameType;
}

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

void hdlc_SendPacket(int arrindex, char hdlcREQframeptr[RES_FRAME_COUNT][MAX_SIZE])
{
  // int i = 0;
  for (int i = 0; i <= Hdlc_OutBuf[2] + 1; i++)
  {
    hdlcREQframeptr[arrindex][i] = Hdlc_OutBuf[i];
  }
}

// char AARQ_Client_Meter_Reader_Password(char passwordkey[])
char AARQ_Client_Meter_Reader_Password()
{
  int i = 0;
  char arrqframe_index = 0;
  char length = 0;
  char passLen;
  char clinetapplicationcontext[] = {0x80, 0x02, 0x02, 0x84};

  char passwordkey[LLS_Keys[METER_MAKE].length() + 1] = {0};

  LLS_Keys[METER_MAKE].toCharArray(passwordkey, (sizeof(passwordkey) / sizeof(passwordkey[0])));

  char password_tag[] = {AARQ_AUTHVALUE, 0x02 + 0x00, 0x80, 0x00};

  AARQFrame[arrqframe_index++] = TAG_AARQ;
  AARQFrame[arrqframe_index++] = LENGTH;
  for (i = 0; i < 4; i++)
    AARQFrame[arrqframe_index++] = clinetapplicationcontext[i];
  for (i = 0; i < 11; i++)
    AARQFrame[arrqframe_index++] = app_ctxt_name_1[i];
  for (i = 0; i < 4; i++)
    AARQFrame[arrqframe_index++] = aARQ_aCSE_rEQs[i];
  for (i = 0; i < 9; i++)
    AARQFrame[arrqframe_index++] = auth_mech_name_1[i];

  password_tag[1] += LLS_Keys[METER_MAKE].length();
  password_tag[3] += LLS_Keys[METER_MAKE].length();

  for (i = 0; i < 4; i++)
  {
    AARQFrame[arrqframe_index++] = password_tag[i];
  }

  for (i = 0; i < ((sizeof(passwordkey) / sizeof(passwordkey[0])) - 1); i++)
  {
    AARQFrame[arrqframe_index++] = passwordkey[i];
  }
  for (i = 0; i < 4; i++)
  {
    AARQFrame[arrqframe_index++] = auth_password_or_public_Tag_len[i];
  }
  for (i = 0; i < 14; i++)
  {
    AARQFrame[arrqframe_index++] = xDlmsRequest1[i];
  }
  AARQFrame[1] = arrqframe_index - 2;

  return arrqframe_index;
}

void DateTimeRange(char Fromdate[], char Todate[], char fromDateTime[], char ToDateTime[])
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
  
  if (MeterDataType == LOAD_PROFILE_DATA)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == INSTANT_DATA)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_instant[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == BILLING_DATA)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_billing[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == EVENTVOLTAGE)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventvoltage[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == EVENTCURRENT)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventcurrent[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
    else if (MeterDataType == EVENTPOWER)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventpower[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == EVENTTRANSACTION)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventtransaction[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
    else if (MeterDataType == EVENTOTHER)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventother[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == EVENTNONROLL)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventnonrollover[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == BILLINGSCALAR)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_Billscalar[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == INSTANTSCALAR)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_InstantScalar[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == LOAD_PROFILE_SCALAR)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_loadprofileScalar[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == LOAD_DATA_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_loaddataobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   LOAD_SCALAR_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_loadscalarobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   INSTANT_DATA_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_instantdataobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   INSTANT_SCALAR_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_instantscalarobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   BILLING_DATA_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_billingdataobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   BILLING_SCALAR_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_billingscalarobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   EVENT_SCALAR_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventscalarobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
   else if (MeterDataType ==   EVENT_SCALAR)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventscalar[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType ==   EVENT_DATA_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_eventdataobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == DAILY_LOAD_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_dlobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == DAILY_LOAD_DATA)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_dldata[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == DL_SCALAR_OBIS)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_dlscalarobis[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else if (MeterDataType == DL_SCALAR_DATA)
  {
    MeterCommandframe_index += MeterCommandUnciperedIframe(Obiscode_dlscalardata[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
  }
  else
  {
    if (PhaseType == SINGLE_PHASE)
    {
      MeterCommandframe_index += MeterCommandUnciperedIframe(INST_Obiscode[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
    }
    else // THREE PHASE
    {
      MeterCommandframe_index += MeterCommandUnciperedIframe(THREE_PH_INST_Obiscode[ObiscodeIndex++], Fromdate, Todate, MeterDataType);
    }
  }
  Iframe[1] = MeterCommandframe_index - 2;
  iframe = &Iframe[0];

  /*Wrapping the data using HDLC wrapper for part1 meter */
  HdlcWrapperEncoding(FrameType, unciperIframe, MeterCommandframe_index);
}


static char MeterCommandUnciperedIframe(char Obiscodes[], char Fromdate[], char Todate[], char MeterDataType)
{
  int i = 0;
  char OutBuf_Index = 0;
  char K_SUCCESS = 0;

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

  if(MeterDataType == BILLING_DATA && bavailflag == 1)
  {
      unciperIframe[OutBuf_Index++] = 0x07;
  }
  else
  {
      unciperIframe[OutBuf_Index++] = Obiscodes[7];
  }

  if (ObiscodeIndex == 1 && (MeterDataType == LOAD_PROFILE_DATA || MeterDataType == DAILY_LOAD_DATA))
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
    // unciperIframe[OutBuf_Index++] = 0x00;
    // unciperIframe[OutBuf_Index++] = 0x1E;//1E

    unciperIframe[OutBuf_Index++] = (char)Fromdate[4]; // 0x06 ;//0x05; //rload->Fromdate[4];
    unciperIframe[OutBuf_Index++] = (char)Fromdate[5]; // 0x30;//rload->Fromdate[5];

    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00; // added 021120 for daily load
    // unciperIframe[OutBuf_Index++] = 0x01;//commented 021120 for daily load
    // unciperIframe[OutBuf_Index++] = 0x4A; //commented 021120 for daily load
    unciperIframe[OutBuf_Index++] = 0x00; // added 021120 for daily load
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

    // unciperIframe[OutBuf_Index++] = 0x17;//17
    // unciperIframe[OutBuf_Index++] = 0x1E;//1e
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00; // added 021120 for daily load
    unciperIframe[OutBuf_Index++] = 0x00; // added 021120 for daily load
    // unciperIframe[OutBuf_Index++] = 0x01; commented 021120 for daily load
    //  unciperIframe[OutBuf_Index++] = 0x4A; commented 021120 for daily load
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = (char)DT_ARRAY;
    unciperIframe[OutBuf_Index++] = 0x00; // length of DT_ARRAY */
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTPOWER && profile_pe_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_pe_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_pe_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1);
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_pe_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTVOLTAGE && profile_ve_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_ve_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_ve_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1);
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_ve_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTCURRENT && profile_ce_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_ce_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_ce_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1); // 0x2D;//0x2D = 45
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_ce_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTTRANSACTION && profile_te_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_te_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_te_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1); // 0x2D;//0x2D = 45
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_te_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTOTHER && profile_oe_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_oe_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_oe_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1); // 0x2D;//0x2D = 45
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_oe_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 1 && MeterDataType == EVENTNONROLL && profile_ne_count > 0)
  {
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x02;
    unciperIframe[OutBuf_Index++] = 0x04;
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
      if(profile_ne_count > 5)
        unciperIframe[OutBuf_Index++] = char(profile_ne_count - 5); // 0x2D;//0x2D = 45
      else
        unciperIframe[OutBuf_Index++] = char(1); // 0x2D;//0x2D = 45
    unciperIframe[OutBuf_Index++] = 0x06;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = char(profile_ne_count); // 0x32;//0x32 = 50
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x01;
    unciperIframe[OutBuf_Index++] = 0x12;
    unciperIframe[OutBuf_Index++] = 0x00;
    unciperIframe[OutBuf_Index++] = 0x00;
  }
  else if (ObiscodeIndex == 4 && MeterDataType == INSTANT_DATA)
  {
    unciperIframe[OutBuf_Index++] = (char)HDLC_Logical_Name;
  }
  else if (MeterDataType == BILLING_DATA)
  {
    if(bavailflag == 1)
    {
      unciperIframe[OutBuf_Index++] = 0x00;
    }
    else
    {
      unciperIframe[OutBuf_Index++] = (byte)DT_ARRAY;
      unciperIframe[OutBuf_Index++] = 0x02;//length of DT_ARRAY
      unciperIframe[OutBuf_Index++] = 0x02;
      unciperIframe[OutBuf_Index++] = 0x04;//length of DT_STRUCTURE
      unciperIframe[OutBuf_Index++] = 0x06;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = readentrycount[0];  //read no // available entries
      unciperIframe[OutBuf_Index++] = 0x06;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = readendcount[0];  //count no
      unciperIframe[OutBuf_Index++] = 0x12;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x01;
      unciperIframe[OutBuf_Index++] = 0x12;
      unciperIframe[OutBuf_Index++] = 0x00;
      unciperIframe[OutBuf_Index++] = 0x00;
    }
  }
  else
  {
    unciperIframe[OutBuf_Index++] = 0x00;
  }

  // for(int tmp = 0 ; tmp < OutBuf_Index ;tmp++)
  // {
  //  Serial2.print(unciperIframe[tmp],HEX);
  //  Serial2.print(" ");
  // }

  return OutBuf_Index;
}
/*LOAD REQUEST FRAMING 02-03-2022*/

int check_responsebuffer(int arrayindex)
{
  if (ResponseBuffer[arrayindex][0] != 0x7E || ResponseBuffer[arrayindex][2] == 0)
  {
    seriallogger_string("NO RESPONSE/INVALID RESPONSE");
    return 1;
  }
  else
  {
    return 0;
  }
}

int AutoDetectMeterType(int arg_REQindex)
{
  seriallogger_string("IN AUTODETECTION");
  int status = 0;
  char DLMS_SNRM[] = {0x09, 0x7E, 0xA0, 0x07, 0x03, 0x41, 0x93, 0x5A, 0x64, 0x7E, '\0'};
  char DLMS_LLS_Capital[] = {0x48, 0x7E, 0xA0, 0x46, 0x03, 0x41, 0x10, 0xC5, 0xD8, 0xE6, 0xE6, 0x00, 0x60, 0x38, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x08, 0x80, 0x06, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x42, 0x5F, 0x7E, '\0'};
  char DLMS_LLS_LT[] = {0x46, 0x7E, 0xA0, 0x44, 0x03, 0x41, 0x10, 0xB3, 0xE1, 0xE6, 0xE6, 0x00, 0x60, 0x36, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x06, 0x80, 0x04, 0x6C, 0x6E, 0x74, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x1F, 0x5E, 0x7E, '\0'};
  char DLMS_LLS_HPL[] = {0x52, 0x7E, 0xA0, 0x50, 0x03, 0x41, 0x10, 0xFE, 0x50, 0xE6, 0xE6, 0x00, 0x60, 0x42, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x12, 0x80, 0x10, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0xA5, 0xED, 0x7E, '\0'};
  char DLMS_LLS_LG[] = {0x4A, 0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x43, 0x8A, 0x7E, '\0'};
  char DLMS_LLS_SECURE[] = {0x4A, 0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x41, 0x42, 0x43, 0x44, 0x30, 0x30, 0x30, 0x31, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x18, 0x1D, 0xFF, 0xFF, 0x8A, 0xC8, 0x7E, '\0'};
  // char DLMS_LLS_GENUS[] = {0x59, 0x7E, 0xA0, 0x57, 0x03, 0x41, 0x10, 0xDF, 0x07, 0xE6, 0xE6, 0x00, 0x60, 0x49, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x03, 0xA6, 0x0A, 0x04, 0x08, 0x47, 0x4F, 0x45, 0x30, 0x30, 0x30, 0x30, 0x30, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x31, 0x41, 0x32, 0x42, 0x33, 0x43, 0x34, 0x44, 0xBE, 0x17, 0x04, 0x15, 0x21, 0x13, 0x20, 0x00, 0x00, 0x00, 0x00, 0x4D, 0x0A, 0x82, 0xD1, 0x8E, 0x20, 0x47, 0xAB, 0xBD, 0xDB, 0xE9, 0xE2, 0x7C, 0x8B, 0xE9, 0xBE, 0x7E, '\0'};
  char DLMS_LLS_GENUS[] = {0x46,0x7E,0xA0,0x44,0x03,0x41,0x10,0xB3,0xE1,0xE6,0xE6,0x00,0x60,0x36,0xA1,0x09,0x06,0x07,0x60,0x85,0x74,0x05,0x08,0x01,0x01,0x8A,0x02,0x07,0x80,0x8B,0x07,0x60,0x85,0x74,0x05,0x08,0x02,0x01,0xAC,0x0A,0x80,0x08,0x31,0x41,0x32,0x42,0x33,0x43,0x34,0x44,0xBE,0x10,0x04,0x0E,0x01,0x00,0x00,0x00,0x06,0x5F,0x1F,0x04,0x00,0x00,0x1E,0x5D,0xFF,0xFF,0xA8,0xAB,0x7E,'\0'};
  char DLMS_LLS_MAXWELL[] = {0x4A, 0x7E, 0xA0, 0x48, 0x03, 0x41, 0x10, 0x87, 0x76, 0xE6, 0xE6, 0x00, 0x60, 0x3A, 0x80, 0x02, 0x02, 0x84, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x6D, 0x78, 0x32, 0x30, 0x31, 0x31, 0x39, 0x39, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x1E, 0x1D, 0xFF, 0xFF, 0x3F, 0xE1, 0x7E, '\0'}; // MAXWELL 04-04-2022
  char DLMS_LLS_EEPL[] = {0x46, 0x7E, 0xA0, 0x44, 0x03, 0x41, 0x10, 0xB3, 0xE1, 0xE6, 0xE6, 0x00, 0x60, 0x36, 0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0x8A, 0x02, 0x07, 0x80, 0x8B, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x02, 0x01, 0xAC, 0x0A, 0x80, 0x08, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0xBE, 0x10, 0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x62, 0x1E, 0x5D, 0xFF, 0xFF, 0x54, 0xB3, 0x7E, '\0'};              // Added on 03-08-2022 for EEPL Meter
  char DLMSCommand_END[] = {0x09, 0x7E, 0xA0, 0x07, 0x03, 0x41, 0x53, 0x56, 0xA2, 0x7E, '\0'};
  char DLMSCommand_MeterType[] = {0x1B, 0x7E, 0xA0, 0x19, 0x03, 0x41, 0x32, 0x3A, 0xBD, 0xE6, 0xE6, 0x00, 0xC0, 0x01, 0xC1, 0x00, 0x01, 0x00, 0x00, 0x5E, 0x5B, 0x09, 0xFF, 0x02, 0x00, 0x52, 0x9E, 0x7E, '\0'};
  char ADMTreqptr[4][MAX_SIZE] = {0};
  int arrayindex = 0;

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  blockcopy(ADMTreqptr, DLMS_SNRM, arrayindex);
  switch (arg_REQindex)
  {
  
  case SECURE:
    blockcopy(ADMTreqptr, DLMS_LLS_SECURE, ++arrayindex);
    break;
  case LG:
    blockcopy(ADMTreqptr, DLMS_LLS_LG, ++arrayindex);
    break;
  case LT:
    blockcopy(ADMTreqptr, DLMS_LLS_LT, ++arrayindex);
    break;    
  case HPL:
    blockcopy(ADMTreqptr, DLMS_LLS_HPL, ++arrayindex);
    break;
  case CAP:
    blockcopy(ADMTreqptr, DLMS_LLS_Capital, ++arrayindex);
    break;
  case GENUS:
    blockcopy(ADMTreqptr, DLMS_LLS_GENUS, ++arrayindex);
    break;
  case MAXWELL:
    blockcopy(ADMTreqptr, DLMS_LLS_MAXWELL, ++arrayindex);
    break;
  case EEPL:
    blockcopy(ADMTreqptr, DLMS_LLS_EEPL, ++arrayindex);
    break;
  }
  blockcopy(ADMTreqptr, DLMSCommand_MeterType, ++arrayindex);
  blockcopy(ADMTreqptr, DLMSCommand_END, ++arrayindex);
  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;
  int count = 0;

  bool meter_found = false;

  for(int metercount=0; metercount < 4; metercount++) 
  {
    int ResByteCount = 0;
    Serial.write(&ADMTreqptr[metercount][0], (ADMTreqptr[metercount][2] + 2));//SNRM
    Serial.flush();
    String request_data = "";
    for (int data_i = 0; data_i < ADMTreqptr[metercount][2] + 2; data_i++)
    {
      request_data += String(ADMTreqptr[metercount][data_i], HEX);
      request_data += " ";
    }
    
    seriallogger_string("TX Count : " + String(metercount));

    seriallogger_string("TX : " + request_data);
    
    delay(1000);
    SerialRead(metercount, ResByteCount);
    delay(500);
    ///////////////////////////Error File creation////////////////
    return_value = check_responsebuffer(metercount);
    if (return_value == 1)
    {
      
      seriallogger_string("METER MAKE DETECTION FAILED_ " + (String)count);
      CreateNoresponseDataFile("01", "METER MAKE DETECTION FAILED_" + request_data);
    }
    //////////////////////Check response status/////////////////////////////////////
    if (metercount == 1) // if it is AARQ Request then
    {
      if ((ResponseBuffer[metercount][25] == 0x03 && ResponseBuffer[metercount][26] == 0x02 && ResponseBuffer[metercount][27] == 0x01 && ResponseBuffer[metercount][28] == 0x00) ||
          (ResponseBuffer[metercount][29] == 0x03 && ResponseBuffer[metercount][30] == 0x02 && ResponseBuffer[metercount][31] == 0x01 && ResponseBuffer[metercount][32] == 0x00))
      {
        METER_MAKE = arg_REQindex;
        seriallogger_string("METER_MAKE " + (String)METER_MAKE);
        meter_found = true;
//        CreateNoresponseDataFile("10", "METER MAKE DETECTION SUCCESS");

      }
      else if ((ResponseBuffer[metercount][25] == 0x03 && ResponseBuffer[metercount][26] == 0x02 && ResponseBuffer[metercount][27] == 0x01) ||
          (ResponseBuffer[metercount][29] == 0x03 && ResponseBuffer[metercount][30] == 0x02 && ResponseBuffer[metercount][31] == 0x01))
      {
        status = 2;
      }
    }

    if(meter_found == true && metercount == 2)
    {
      ParseMeterCategoryType(ResponseBuffer);
      status = 1;
    }
    ////////////////////////////////////////////////////////////////////////////////
  }
   
  return status;
}

void blockcopy(char destarray[4][MAX_SIZE], char srcarray[], int arrindex)
{
  for (int i = 0; i <= (int)(srcarray[0] - 1); i++)
  {
    destarray[arrindex][i] = srcarray[i + 1];
  }
}
/*ADMT 02-03-2022*/

/*INST REQ FRAMING 03-03-2022*/
int ReadMeterConfig(char REQframeptr[][MAX_SIZE])
{
  int ChoppedByteCount = 0;
  int i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  int no_of_Req = 0;
  char MeterDataType = METERCONFIG_DATA;
  memsetbuffer(AARQFrame, sizeof(AARQFrame));
  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, REQframeptr);
  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, REQframeptr);

  // 04-04-2022
  GetSequenceNumber(0);

  if (PhaseType == SINGLE_PHASE)
    no_of_Req = SINGLE_PH_PARAM_COUNT;
  else
    no_of_Req = THREE_PH_PARAM_COUNT;

  for (i = 0; i < no_of_Req; i++)
  {
    MeterCommandFrame(NULL, NULL, MeterDataType);

    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, REQframeptr);
  }

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, REQframeptr);
  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;

  /*Read Send and Read Response from meter here. Response will be added into ResponseBuffer Global buffer.*/
  for (int reqIndex = 0; reqIndex < (no_of_Req + ASSC_REQ_COUNT); reqIndex++)
  {
    int ResByteCount = 0;

    for (int j = 0; j < (REQframeptr[reqIndex][2] + 2); j++)
    {
      seriallogger((REQframeptr[reqIndex][j]));
    }
    seriallogger('\n');

    Serial.write(&REQframeptr[reqIndex][0], (REQframeptr[reqIndex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      // Serial2.println();
      Serial2.print("TX : ");
      for (int i = 0; i < REQframeptr[reqIndex][2] + 2; i++)
      {
        Serial2.print(REQframeptr[reqIndex][i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();

    }
    SerialRead(reqIndex, ResByteCount);

    return_value = check_responsebuffer(reqIndex);

    if (return_value == 1)
    {
//      CreateNoresponseDataFile("03", "ReadMeterConfig failed");
      return 0;
    }
    if (reqIndex == 1) 
    {
      if ((ResponseBuffer[reqIndex][25] == 0x03 && ResponseBuffer[reqIndex][26] == 0x02 && ResponseBuffer[reqIndex][27] == 0x01 && ResponseBuffer[reqIndex][28] == 0x00) ||
          (ResponseBuffer[reqIndex][29] == 0x03 && ResponseBuffer[reqIndex][30] == 0x02 && ResponseBuffer[reqIndex][31] == 0x01 && ResponseBuffer[reqIndex][32] == 0x00))
      {
//        CreateNoresponseDataFile("20", "METER CONFIG SUCCESS");
      }
      else
      {
//        CreateNoresponseDataFile("21", "METER CONFIG FAILURE");
        return 0;
      }
    }
  }

  ChoppedByteCount = ChopInstMeterResponse(ResponseBuffer);
  if(ChoppedByteCount == 0)
  {
    return 0;
  }

  return 1;
}
/*INST REQ FRAMING 03-03-2022*/

/*READ METER DATE TIME ONLY 08-03-2022*/
// void InitialiseESP32RTC(/*char REQframeptr[][MAX_SIZE]*/)
int InitialiseESP32RTC()
{
  delay(1000);
  char Meter_RTC_REQframeptr[4][MAX_SIZE] = {0};
  int i = 0;
  int arrindex = 0;
  int no_of_Req = 0;
  char MeterDataType = METERCONFIG_DATA;
  // Get_Scalar_Flag = FALSE;
  memsetbuffer(AARQFrame, sizeof(AARQFrame));
  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, Meter_RTC_REQframeptr);
  arrqframe_index = AARQ_Client_Meter_Reader_Password();
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, Meter_RTC_REQframeptr);

  // 04-04-2022
  GetSequenceNumber(0);
  // Serial2.print("RTC ")
  for (i = 0; i < METER_RTC_READ_REQ_COUNT; i++)
  {
    MeterCommandFrame(NULL, NULL, MeterDataType);
    hdlc_SendPacket(++arrindex, Meter_RTC_REQframeptr);
  }

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, Meter_RTC_REQframeptr);
  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;

  /*Read Send and Read Response from meter here. Response will be added into ResponseBuffer Global buffer.*/
  for (int reqIndex = 0; reqIndex < (sizeof(Meter_RTC_REQframeptr) / sizeof(Meter_RTC_REQframeptr[0])); reqIndex++)
  {
    int ResByteCount = 0;
    Serial.write(&Meter_RTC_REQframeptr[reqIndex][0], (Meter_RTC_REQframeptr[reqIndex][2] + 2));
    Serial.flush();

    if (METER_DEBUG == TRUE)
    {
      // Serial2.println();
      Serial2.print("TX : ");
      for (int i = 0; i < Meter_RTC_REQframeptr[reqIndex][2] + 2; i++)
      {
        Serial2.print(Meter_RTC_REQframeptr[reqIndex][i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();
    }
    
    int readBytes = SerialRead(reqIndex, ResByteCount);

    if (readBytes > 0)
    {
      // BREAK METER READING OF NO RESPONSE FROM METER
      if (ResponseBuffer[reqIndex][0] != 0x7E || ResponseBuffer[reqIndex][2] == 0)
        return 0;
    }
    if (reqIndex == 1) 
    {
      if ((ResponseBuffer[reqIndex][25] == 0x03 && ResponseBuffer[reqIndex][26] == 0x02 && ResponseBuffer[reqIndex][27] == 0x01 && ResponseBuffer[reqIndex][28] == 0x00) ||
          (ResponseBuffer[reqIndex][29] == 0x03 && ResponseBuffer[reqIndex][30] == 0x02 && ResponseBuffer[reqIndex][31] == 0x01 && ResponseBuffer[reqIndex][32] == 0x00))
      {
//        CreateNoresponseDataFile("20", "METER RTC SUCCESS");
      }
      else
      {
//        CreateNoresponseDataFile("21", "METER RTC FAILURE");
        return 0;
      }
    }

  }

  /*Parse and initialise RTC here*/
  DateTimeParsing(ResponseBuffer);

  if ((rtc.getMonth() > 12) || (rtc.getDay() == 0 || rtc.getDay() > 31) || rtc.getHour() > 23 || rtc.getMinute() > 59 || rtc.getSecond() > 59 || rtc.getYear() < 2022 || rtc.getYear() <= 0)
  {
//    CreateNoresponseDataFile("22", "RECEIVED RTC FAILURE");
    return 0;
  }

  return 1;
}
/*READ METER DATE TIME ONLY 03-03-2022*/

// Version 5
int ClearResponseBuffer()
{
    send_disconnect_command_to_serial();

  
  for (int j = 0; j < MAX_SIZE_RESPONSE_BUFFER; j++)
  {
    for (int i = 0; i < RES_FRAME_COUNT; i++)
    {
      ResponseBuffer[i][j] = 0;
    }
  }
  return 1;
}
// Version 5

/*WRITE INTO FILE*/
void WriteIntoFile(String WriteFileName, char FileContent[][MAX_SIZE], int FileContentSize)
{
  LittleFS.remove(WriteFileName);
  File file = LittleFS.open(WriteFileName, "a");

  if (!file)
  {
    return;
  }

  for (int i = 0; i < FileContentSize; i++)
  {
    for (int j = 0; j < (FileContent[i][2] + 2); j++)
    {
      file.print((FileContent[i][j]), HEX);
      file.print(" ");
    }
    file.println();
  }

  file.close();
}
/*WRITE INTO FILE*/

/*READ FROM FILE*/
int ReadFromFile(String ReadFileName)
{
  // File file2 = LittleFS.open(ReadFileName);
  File file2 = LittleFS.open(ReadFileName, "r");

  if (!file2)
  {
    // seriallogger_string("Failed to open file for reading");
    seriallogger_string("Failed to open file for reading");
    return 0;
  }

  char bufferc[1024]; // 30-03-2022
  String line = ""; // 30-03-2022
  int line_index = 0; // 30-03-2022

  while (file2.available())
  {
    // 30-03-2022
    int a = file2.readBytesUntil('\n', bufferc, sizeof(bufferc));
    bufferc[a] = 0;
    BlockIDs_Buffer[line_index] = bufferc;
    ////seriallogger_string(BlockIDs_Buffer[line_index]);
    line_index++;
    ////seriallogger_string(line);
  }

  file2.close();

  return line_index;
}
/*READ FROM FILE*/

/*READ FROM SERIAL*/
int SerialRead(int reqIndex, int ResByteCount)
{
  int wait_count = 0;
  int data_available = 0;
  String commanddata = "";
  // RTC();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println("");
    Serial2.print("RES: ");
  }
  digitalWrite(DATA_COMMUNICATION, LOW);

  while (Serial.available() >= 0)
  {
    if (Serial.available())
    {
      data_available = 1; 
      wait_count = 0;
      incomingByte = Serial.read();
      digitalWrite(DATA_COMMUNICATION, HIGH);
      ResponseBuffer[reqIndex][ResByteCount++] = (char)incomingByte;
      if (METER_DEBUG == TRUE)
      {
        Serial2.print(incomingByte, HEX);
        Serial2.print(" ");
      }
    }
    // else if(data_available == 1)
    // {
    //   break;
    // }
    else
    {
      wait_count++;
      if (wait_count > 5)
      { 
        break;
      }
      delay(400);
    }

    if(data_available == 1 && (Serial.available() == 0))
    {

      delay(1000);      
      if(Serial.available()==0)
      {
        break;
      }

    }
  }
  digitalWrite(DATA_COMMUNICATION, LOW);
  return ResByteCount;
}
/*PARSE METER RTC*/
void DateTimeParsing(char ResponseBuffer[][MAX_SIZE_RESPONSE_BUFFER])
{
  int local_year = 0;
  byte local_month = 0;
  byte local_day = 0;
  byte local_hour = 0;
  byte local_mins = 0;
  byte local_sec = 0;
  int startColumnIndex = 17;
  int startRowIndex = 2;
  g_year = local_year = (int)((ResponseBuffer[startRowIndex][startColumnIndex] << 8) | (ResponseBuffer[startRowIndex][startColumnIndex + 1]));
  g_month = local_month = ResponseBuffer[startRowIndex][startColumnIndex + 2];
  g_day = local_day = ResponseBuffer[startRowIndex][startColumnIndex + 3];
  g_startingHour = g_hours = local_hour = ResponseBuffer[startRowIndex][startColumnIndex + 5];
  g_minutes = local_mins = ResponseBuffer[startRowIndex][startColumnIndex + 6];
  g_seconds = local_sec = ResponseBuffer[startRowIndex][startColumnIndex + 7];

  // rtc.setTime(55, 59, 13, 9, 3, 2022);  // 09th Mar 2022 13:59:55 //ASSIGN OBTAINED RTC FROM METER TO ESP32 HERE
  rtc.setTime(local_sec, local_mins, local_hour, local_day, local_month, local_year); // Commented on 25-03-2022 as ESP8266  doesn't have internal RTC.
  // seriallogger_string("\r\nDONE WITH DT PARSING\r\n");
  // g_hours = 10;g_minutes = 57;
  // String sync_RTC = (String)/*rtc.getYear()*/g_year + "-" + (String)/*(rtc.getMonth()+1)*/g_month + "-" + (String)/*rtc.getDay()*/g_day + " " + (String)/*rtc.getHour()*/g_hours + ":" + (String)/*rtc.getMinute()*/g_minutes + ":" + (String)/*rtc.getSecond()*/g_seconds;
   String sync_RTC = (String)local_year + "-" + (String)(local_month ) + "-" + (String)local_day + " " + (String)local_hour + ":" + (String)local_mins + ":" + (String)local_sec;
  seriallogger_string("Sync Date Time: " + sync_RTC);
}
/*PARSE METER RTC*/

/*PARSE METER CATEGORY TYPE*/
void ParseMeterCategoryType(char ResponseBuffer[][MAX_SIZE_RESPONSE_BUFFER])
{
  int startColumnIndex = 0; // 16 for HPL and L&T Meters and SECURE //17 for MAXWELL

  if (ResponseBuffer[2][15] == 0x11)
    startColumnIndex = 16;
  else
    startColumnIndex = 17;

  MeterCategoryType = ResponseBuffer[2][startColumnIndex];

  if (MeterCategoryType == 5 || MeterCategoryType == 6) // SINGLE PHASE AC STATIC METERS
  {
    PhaseType = 1;
    meter_type = 1;
  }
  else
  {
    PhaseType = 3; // THREE PHASE METERS
    meter_type = 3;
  }

  if (METER_MAKE == LG)
  {
    PhaseType = 3; // THREE PHASE METERS
  }

  seriallogger_string("Meter Category Type: " + (String)MeterCategoryType);
  seriallogger_string("Phase = " + (String)PhaseType);
}
/*PARSE METER CATEGORY TYPE*/

/*CHOP INTANTANEOUS METER RESPONSE*/
int ChopInstMeterResponse(char ResponseBuffer[][MAX_SIZE_RESPONSE_BUFFER])
{
  int temp_index = 0; // Version 3 Code
  int temp_PFindex = 0;
  int no_of_Res = 0;
  int startRowIndex = 2;
  int startColumnIndex = 15;
  int choppedBufIndex = 0;
  int temp_MSN_Index = 0;
  MeterSerialNo_Final = "";

  if (PhaseType == SINGLE_PHASE)
    no_of_Res = SINGLE_PH_PARAM_COUNT;
  else if (PhaseType == THREE_PHASE)
    no_of_Res = THREE_PH_PARAM_COUNT;

  for (int resIndex = startRowIndex; resIndex < (no_of_Res + 2); resIndex++)
  {
    temp_PFindex = 0;
    for (int resColumnIndex = startColumnIndex; resColumnIndex < ((ResponseBuffer[resIndex][2] + 2) - 3); resColumnIndex++, choppedBufIndex++)
    {
      Chopped_Inst_DataBuffer[choppedBufIndex] = ResponseBuffer[resIndex][resColumnIndex];

      if (resIndex == FRAME_INST_PCT)
      {
        ProfileCaptureBytes[temp_index++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_MSN)
      {
        if (ResponseBuffer[resIndex][startColumnIndex] == 0x06) // Unsigned Long
        {
          {
            ParsedMeterSerialNo = ((ParsedMeterSerialNo << 8) | ResponseBuffer[resIndex][resColumnIndex]);
            MeterSerialNo_Final = (String)ParsedMeterSerialNo;
          }
        }
        else if ((ResponseBuffer[resIndex][startColumnIndex] == 0x09 || ResponseBuffer[resIndex][startColumnIndex] == 0x0A) && resColumnIndex >= (startColumnIndex + 2)) // OCTET STRING
        {
          char temp_MSN[ResponseBuffer[resIndex][startColumnIndex + 1]];
          temp_MSN[temp_MSN_Index++] = ResponseBuffer[resIndex][resColumnIndex];
          temp_MSN[temp_MSN_Index] = '\0';

          String temp = temp_MSN;
          MeterSerialNo_Final = (String)temp;
        }
      }
      else if (resIndex == FRAME_INST_VECNT)
      {
        ProfileVEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_CECNT)
      {
        ProfileCEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_PECNT)
      {
        ProfilePEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_TECNT)
      {
        ProfileTEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_OECNT)
      {
        ProfileOEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
      else if (resIndex == FRAME_INST_NECNT)
      {
        ProfileNEBytes[temp_PFindex++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
      }
    }
  }

  profile_capture_time = ParseMeterDT_DATA(ProfileCaptureBytes);
  profile_ve_count = ParseMeterDT_DATA(ProfileVEBytes);
  profile_ce_count = ParseMeterDT_DATA(ProfileCEBytes);
  profile_pe_count = ParseMeterDT_DATA(ProfilePEBytes);
  profile_te_count = ParseMeterDT_DATA(ProfileTEBytes);
  profile_oe_count = ParseMeterDT_DATA(ProfileOEBytes);
  profile_ne_count = ParseMeterDT_DATA(ProfileNEBytes);
  seriallogger_string("The Profile time is : " +String(profile_capture_time));
  seriallogger_string("The voltage count is : " +String(profile_ve_count));
  seriallogger_string("The current count is : " +String(profile_ce_count));
  seriallogger_string("The power count is : " +String(profile_pe_count));
  seriallogger_string("The trans count is : " +String(profile_te_count));
  seriallogger_string("The other count is : " +String(profile_oe_count));
  seriallogger_string("The non roll over count is : " +String(profile_ne_count));


  if(MeterSerialNo_Final == "NILL" || MeterSerialNo_Final == "")
  {
    return 0;
  }
  return 1;
}

/*CHOP INTANTANEOUS METER RESPONSE*/

/*CHOP INTANTANEOUS SCALAR METER RESPONSE 14-04-2022*/
int ChopInstScalarMeterResponse(char ResponseBuffer[][MAX_SIZE_RESPONSE_BUFFER])
{
  int temp_index = 0; // Version 3 Code
  int no_of_Res = 0;
  int startRowIndex = 2;
  int startColumnIndex = 15;
  int choppedBufIndex = 0;
  int temp_MSN_Index = 0;
  if (PhaseType == SINGLE_PHASE)
    no_of_Res = SINGLE_PH_PARAM_COUNT;
  else if (PhaseType == THREE_PHASE)
    no_of_Res = THREE_PH_PARAM_COUNT;

  for (int resIndex = startRowIndex; resIndex < (no_of_Res + 2); resIndex++)
  {
    for (int resColumnIndex = startColumnIndex; resColumnIndex < ((ResponseBuffer[resIndex][2] + 2) - 3); resColumnIndex++, choppedBufIndex++)
    {
      Chopped_Inst_Scalar_DataBuffer[choppedBufIndex] = ResponseBuffer[resIndex][resColumnIndex];

      // Version 3 Code Block
      if (resIndex == 8) // kWh Response Frame
      {
        kWhScalarBytes[temp_index++] = (byte)ResponseBuffer[resIndex][resColumnIndex];
        /*seriallogger(kWhScalarBytes[temp_index-1]);
        seriallogger('\n');*/
      }
      // Version 3 Code Block
    }
  }

  // seriallogger_string();
  // seriallogger_string("INST SCALAR DATA: ");
  // for (int i = 0; i < choppedBufIndex; i++)
  // {
  //  // Serial2.print(Chopped_Inst_Scalar_DataBuffer[i], HEX);
  //  // Serial2.print(" ");
  // }
  // seriallogger_string();
  return (choppedBufIndex);
}
/*CHOP INTANTANEOUS SCALAR METER RESPONSE 14-04-2022*/

/*CHOP Load METER RESPONSE*/
int ChopLoadMeterResponse(char ResponseBuffer[][MAX_SIZE_RESPONSE_BUFFER], int req_count)
{
  int ChoppedByteCount = 0;
  int no_of_Res = req_count; // 7;
  int startRowIndex = 2;     // 14-04-2022 chnaged from 5 to 2
  int startColumnIndex = 15;
  int choppedBufIndex = 0;
  bool SUPERVISORY_RES = false;

  for (int resIndex = startRowIndex; resIndex < (no_of_Res - 1); resIndex++)
  {
    for (int resColumnIndex = startColumnIndex; resColumnIndex < ((ResponseBuffer[resIndex][2] + 2) - 3); resColumnIndex++, choppedBufIndex++)
    {
      if (SUPERVISORY_RES)
        Chopped_Load_DataBuffer[choppedBufIndex] = ResponseBuffer[resIndex][resColumnIndex];
      else if (ResponseBuffer[resIndex][12] == 0x01)
        Chopped_Load_DataBuffer[choppedBufIndex] = ResponseBuffer[resIndex][resColumnIndex];
      else
        Chopped_Load_DataBuffer[choppedBufIndex] = ResponseBuffer[resIndex][resColumnIndex + 6];
    }
    // seriallogger_string(choppedBufIndex);
    if (ResponseBuffer[resIndex][1] == 0xA8)
    {
      // seriallogger_string("SUPER TRUE: " + (String)resIndex);
      SUPERVISORY_RES = true;
      startColumnIndex = 8;
    }
    else
    {
      Chopped_Load_DataBuffer[choppedBufIndex++] = 0x2A; // 14-04-2022
      SUPERVISORY_RES = false;
      startColumnIndex = 15;
    }
  }

  // Pavan added on 28-07-2022 to validate data. Version 6.1
  if (Chopped_Load_DataBuffer[0] == 42 && Chopped_Load_DataBuffer[1] == 42 && (Chopped_Load_DataBuffer[2] == 42 && Chopped_Load_DataBuffer[3] == 42))
  {
    choppedBufIndex = 0;
  }

  return (choppedBufIndex);
}
/*CHOP Load METER RESPONSE*/

/*WRITE INTO BLOCK ID FILE*/ // 30-03-2022
void WriteIntoBlockIDFile(String WriteFileName, String FileContent[], int FileContentSize)
{
  File file = LittleFS.open(WriteFileName, "w");

  seriallogger_string("FILE NAME:" + WriteFileName);

  if (!file)
  {
    // seriallogger_string("There was an error opening the file for writing");
    seriallogger_string("There was an error opening the file for writing");
    return;
  }

  ////seriallogger_string(FileContentSize);

  for (int i = 0; i < FileContentSize; i++)
  {
    file.println((FileContent[i]));
  }

  file.close();
}
/*WRITE INTO BLOCK ID FILE*/

/*WRITE POST DATA INTO BLOCK ID FILE*/ // 30-03-2022
void WritePostDataIntoBlockIDFile(String WriteFileName, String FileContent)
{
  /*if (!LittleFS.begin()) {
    //seriallogger_string("An Error has occurred while mounting LittleFS");
    seriallogger_string("An Error has occurred while mounting LittleFS");
    return;
  }*/

  if (FileContent.length() <= 0)
    return;

  // IF EXISTS, REMOVE THE FILE 13-04-2022
  /*if(LittleFS.exists(WriteFileName))
  {
    LittleFS.remove(WriteFileName);
  }*/

  File file = LittleFS.open(WriteFileName, "w");

  ////seriallogger_string(WriteFileName);
  if (!file)
  {
    // seriallogger_string("There was an error opening the file for writing");
    seriallogger_string("There was an error opening the file for writing");
    return;
  }
  // file.println(FileContent);

  if (file.print(FileContent))
  {
    // seriallogger_string("File was written");
    seriallogger_string("File was written");
  }
  else
  {
    // seriallogger_string("File write failed");
    seriallogger_string("File write failed");
  }
  file.close();
}
/*WRITE POST DATA INTO BLOCK ID FILE*/

/*READ LOAD PROFILE BLOCK*/
bool ReadLoadProfileData(int a_hour, int a_minutes, int a_day, int a_month, int a_year)
{
  char fromDateTime[14]; // = "100003032022";
  char ToDateTime[14];   // = "110003032022";
  char temp[12];
  sprintf(fromDateTime, "%02s", (String)(a_hour));

  // if (METER_MAKE == LT)                       // Version 3
  // sprintf(temp, "%02s", (String)a_minutes); // MAXWELL //Version 3
                        // else                                        // Version 3
  sprintf(temp, "%02s", (String)0);         // Version 3

  strcat(fromDateTime, temp); // minute
  sprintf(temp, "%02s", (String)a_day);
  strcat(fromDateTime, temp);
  sprintf(temp, "%02s", (String)(a_month));
  strcat(fromDateTime, temp);
  sprintf(temp, "%04s", (String)a_year);
  strcat(fromDateTime, temp);
  // seriallogger_string(fromDateTime);
  seriallogger_string((String)fromDateTime);
  // seriallogger_string("\r\n");

  sprintf(ToDateTime, "%02s", (String)(a_hour));

  // if (METER_MAKE == LT)
  // sprintf(temp, "%02s", (String)a_minutes); // MAXWELL
  // else
    sprintf(temp, "%02s", (String)59);

  strcat(ToDateTime, temp); // minute
  sprintf(temp, "%02s", (String)a_day);
  strcat(ToDateTime, temp);
  sprintf(temp, "%02s", (String)(a_month));
  strcat(ToDateTime, temp);
  sprintf(temp, "%04s", (String)a_year);
  strcat(ToDateTime, temp);
  // seriallogger_string(ToDateTime);
  seriallogger_string((String)ToDateTime);

  bool load_response = false;
  int load_res_count = 0;
  int Load_ChoppedByteCount = 0;

  while(!load_response)
  {
    Load_ChoppedByteCount = temp_LoadReqFrame(/*REQframeptr,*/ fromDateTime, ToDateTime);

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }//End while(!load_response)

  if (Load_ChoppedByteCount == 1) // Added on 28-07-2022 to validate minimum no. of bytes got after chopping responses. Version 6.1
  {
    return CreateIPLDataFile(LOAD_PROFILE_DATA, a_day, a_hour, a_minutes, a_month, a_year); 
  }
  else
  {
    return false;
  }
}
/*READ LOAD PROFILE BLOCK*/

/*CREATE AND WRITE INST DATA FILE*/
void CreateInstDataFile(int Inst_ChoppedByteCount, int Inst_Scalar_ChoppedByteCount)
{
  char temp[5];
  String FinalInst_str = "$";
  FinalInst_str += global_NodeID;
  FinalInst_str += "_";
  FinalInst_str += (String)PhaseType;
  FinalInst_str += "_";
  FinalInst_str += "I";
  FinalInst_str += "_";
  FinalInst_str += MeterSerialNo_Final;
  FinalInst_str += "_";
  // seriallogger_string("\r\n");
  // seriallogger_string(FinalInst_str);
  for (int i = 0; i < Inst_ChoppedByteCount; i++)
  {
    FinalInst_str += (uint8_t)Chopped_Inst_DataBuffer[i];
    FinalInst_str += " ";
  }
  FinalInst_str.trim();
  FinalInst_str += "*"; // 14-04-2022 replaced $ with *

  // 14-04-2022
  for (int i = 0; i < Inst_Scalar_ChoppedByteCount; i++)
  {
    FinalInst_str += (uint8_t)Chopped_Inst_Scalar_DataBuffer[i];
    FinalInst_str += " ";
  }
  FinalInst_str.trim();
  FinalInst_str += "$";

  String Inst_Data_FIle_With_BlockID = "";

  if (rtc.getAmPm(true).equals("pm") && rtc.getHour() != 12)
    sprintf(temp, "%02s", (String)(rtc.getHour() + 12));
  else
    sprintf(temp, "%02s", (String)(rtc.getHour()));
  // sprintf(temp, "%02s", (String)(g_hours));

  Inst_Data_FIle_With_BlockID = "/OBSC"; // 13-04-2022
  Inst_Data_FIle_With_BlockID += "/";
  Inst_Data_FIle_With_BlockID += temp; // BlockID
  Inst_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)rtc.getDay());
  Inst_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)rtc.getMonth() + 1);
  Inst_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%04s", (String)rtc.getYear());
  Inst_Data_FIle_With_BlockID += temp;
  Inst_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)rtc.getHour());
  Inst_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)rtc.getMinute());
  Inst_Data_FIle_With_BlockID += temp;

  Inst_Data_FIle_With_BlockID += "_";
  Inst_Data_FIle_With_BlockID += "I.txt";

  seriallogger_string("Inst BlockID FILE NAME: " + Inst_Data_FIle_With_BlockID);
  // seriallogger_string("\r\n");

  WritePostDataIntoBlockIDFile(Inst_Data_FIle_With_BlockID, FinalInst_str); // 88888888
  // ReadFromFile(Inst_Data_FIle_With_BlockID);

  // Version 3
  // Code to validate whether data has been written into file properly
  String temp_data_string_for_validation = ReadMSNFromFile(Inst_Data_FIle_With_BlockID);

  if (temp_data_string_for_validation.startsWith("$"))
  {
    temp_data_string_for_validation.trim();
    if (temp_data_string_for_validation.endsWith("$"))
    {
      WriteIntoFile("/InstDataStatus.txt", Inst_Data_FIle_With_BlockID);
    }
    else
    {
      LittleFS.remove(Inst_Data_FIle_With_BlockID);
      LittleFS.remove("/InstDataStatus.txt");
    }
  }
  else
  {
    LittleFS.remove(Inst_Data_FIle_With_BlockID);
    LittleFS.remove("/InstDataStatus.txt");
  }
}
/*CREATE AND WRITE INST DATA FILE*/

/*CREATE AND WRITE LOAD DATA FILE*/
bool CreateIPLDataFile(int arg_Profile, int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year) // added arg_month on 16-06-2022 //added arg_year on 18-06-2022
{
  char temp[5] = {0};
  char temp_BlockID[5] = {0};
  sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
  String Load_Data_FIle_With_BlockID = "";
  String FinalLoad_str = "$";
  FinalLoad_str += global_NodeID;
  FinalLoad_str += "_";
  FinalLoad_str += (String)PhaseType;
  FinalLoad_str += "_";
  
  if(arg_Profile == INSTANT_DATA)
    FinalLoad_str += "IP";
  else if(arg_Profile == EVENTVOLTAGE)
    FinalLoad_str += "VE";
  else if(arg_Profile == EVENTCURRENT)
    FinalLoad_str += "CE";
  else if(arg_Profile == EVENTPOWER)
    FinalLoad_str += "PE";
  else if(arg_Profile == EVENTTRANSACTION)
    FinalLoad_str += "TE";
  else if(arg_Profile == EVENTOTHER)
    FinalLoad_str += "OE";
  else if(arg_Profile == EVENTNONROLL)
    FinalLoad_str += "NE";
  else if(arg_Profile == LOAD_PROFILE_DATA)
    FinalLoad_str += "L";
  
  FinalLoad_str += "_";
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  FinalLoad_str += MeterSerialNo_Final;
  FinalLoad_str += "_";
  //Adding Data
  FinalLoad_str += global_frame;

  FinalLoad_str.trim();
  FinalLoad_str += "$";

  Load_Data_FIle_With_BlockID = "/IPL"; // 13-04-2022
  Load_Data_FIle_With_BlockID += "/";

  sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)arg_month);
  Load_Data_FIle_With_BlockID += temp;
  // sprintf(temp, "%04s", (String)arg_year);
  // Load_Data_FIle_With_BlockID += temp;
  Load_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)g_hours);
  Load_Data_FIle_With_BlockID += temp;

  sprintf(temp, "%02s", (String)arg_minute);
 
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";
  
  if(arg_Profile == INSTANT_DATA)
    Load_Data_FIle_With_BlockID += "IP.txt";
  else if(arg_Profile == LOAD_PROFILE_DATA)
    Load_Data_FIle_With_BlockID += "L.txt";
  else if(arg_Profile == EVENTVOLTAGE)
    Load_Data_FIle_With_BlockID += "VE.txt";
  else if(arg_Profile == EVENTCURRENT)
    Load_Data_FIle_With_BlockID += "CE.txt";
  else if(arg_Profile == EVENTPOWER)
    Load_Data_FIle_With_BlockID += "PE.txt";
  else if(arg_Profile == EVENTTRANSACTION)
    Load_Data_FIle_With_BlockID += "TE.txt";
  else if(arg_Profile == EVENTOTHER)
    Load_Data_FIle_With_BlockID += "OE.txt";
  else if(arg_Profile == EVENTNONROLL)
    Load_Data_FIle_With_BlockID += "NE.txt";
  seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
  WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);
  seriallogger_string("The Data is : "+FinalLoad_str);
  // Version 3
  // Code to validate whether data has been written into file properly
  String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);

  if (temp_load_data_string_for_validation.startsWith("$"))
  {
    temp_load_data_string_for_validation.trim();
    if (temp_load_data_string_for_validation.endsWith("$"))
      return true;
    else
    {
      LittleFS.remove(Load_Data_FIle_With_BlockID);
      return false;
    }
  }
  else
  {
    LittleFS.remove(Load_Data_FIle_With_BlockID);
    return false;
  }
}
/*CREATE AND WRITE LOAD DATA FILE*/

/*READ Meter Sl No + RTC + Profile capture period + power off count + voltage event count*/
void ReadMeterDetails()
{
  int total_no_req = 0;
  if (PhaseType == SINGLE_PHASE)
    total_no_req = SINGLE_PH_PARAM_COUNT + ASSC_REQ_COUNT;
  else
    total_no_req = THREE_PH_PARAM_COUNT + ASSC_REQ_COUNT;
  char INST_REQframeptr[total_no_req][MAX_SIZE] = {0};
  
  ///////////////////////////////////////////////////////////////////
  
  int Inst_ChoppedByteCount = 0;
  
  int max_count = 0;
  bool retry_again = false ;

  while(!retry_again)
  {
    Inst_ChoppedByteCount = ReadMeterConfig(&INST_REQframeptr[0]);

    if(Inst_ChoppedByteCount == 1 || max_count > 2)
    {
      retry_again = true;
    }
    else
    {
      max_count++;
    }
  }
  /////////////////////////////////////////////////////////////////

  // if (Inst_ChoppedByteCount == 0)
  //   return;

  MeterSerialNo_Final.trim();

  seriallogger_string("METER SERIAL NUMBER: " + MeterSerialNo_Final);

  // if (MeterSerialNo_Final.length() == 0 /*|| (CheckForInstDataStatus())*/) // IF METER SERIAL NUMBER IS NOT AVAILABLE OR IF INST DATA IS ALREADY READ. DONT PROCEED FURTHER
  //   return;

  CheckForMeterChange(MeterSerialNo_Final);
}
/*READ INST PROFILE*/

void ReadMissingLoadProfileBlock()
{
  bool any_block_read = false; // Version 5.2
  int breakLoop = 0;       // Version 5
  int Maxwell_loopCount = 0;   // Version 3
  int local_minutes = 0;     // Version 3
  char local_temp_Char_Array[4] = {0};
  int temp_hour = g_hours;
  int temp_day = 0;
  int temp_month = 0; // 16-06-2022
  int temp_year = 0;  // 18-06-2022
  if (rtc.getAmPm(true).equals("pm") && rtc.getHour() != 12)
    temp_hour = rtc.getHour() + 12;
  else
    temp_hour = rtc.getHour();

  String fileName, temp_fileName;
  // Dir dir = LittleFS.openDir("/blkstatus");
  File dir = LittleFS.open("/blkstatus");

  File file = dir.openNextFile();
  while (file)
  {
    temp_fileName = "";
    fileName = "";

    temp_fileName += file.name();
    fileName = "/blkstatus";
    fileName += "/";
    fileName += temp_fileName;

    seriallogger_string("READ MISSING BLOCK: " + temp_fileName);

    temp_day = getValue(temp_fileName, '-', 0).toInt();   // 24-06-2022
    temp_month = getValue(temp_fileName, '-', 1).toInt(); // 16-06-2022
    temp_year = getValue(temp_fileName, '-', 2).toInt();  // 18-06-2022

    seriallogger_string("FILE DAY  : " + (String)temp_day);
    seriallogger_string("FILE MONTH: " + (String)temp_month);
    seriallogger_string("FILE YEAR : " + (String)temp_year);

    int fileline_count = ReadFromFile(fileName);

    seriallogger_string("\r\nFILE LINE COUNT: " + (String)fileline_count + "\r\n");

    for (int blockindex = 0; blockindex < fileline_count; blockindex++)
    {
      // String BlockID_Status = BlockIDs_Buffer[blockindex].substring(0, 2);//00|23
      String BlockID_Status = getValue(BlockIDs_Buffer[blockindex], '|', 0); // 00|23 //24-06-2022

      int int_BlockID_Status = BlockID_Status.toInt();

      if (!int_BlockID_Status)
      {
        // Maxwell_loopCount = 0;
        // do
        // {
        //   Maxwell_loopCount++;
          // String BlockID_No = BlockIDs_Buffer[blockindex].substring(3);//00|23
          String BlockID_No = getValue(BlockIDs_Buffer[blockindex], '|', 1); // 00|23 //24-06-2022

          int int_BlockID_No = BlockID_No.toInt();

          seriallogger_string((String)int_BlockID_No + ", " + (String)temp_hour + ", " + (String)temp_day + ", " + (String)g_day);

          if ((((int_BlockID_No < temp_hour) && (temp_day == g_day)) || (temp_day < g_day)) || (temp_month < g_month) || (temp_year == (g_year - 1))) // 16-06-2022
          {

            // if (Maxwell_loopCount <= 2)
            // {
            //   if (Maxwell_loopCount == 1)
            //     local_minutes = 0;
            //   else if (Maxwell_loopCount == 2)
            //     local_minutes = 30;

              bool data_status_flag = ReadLoadProfileData(int_BlockID_No, local_minutes, temp_day, temp_month, temp_year); // 04-04-2022

              if (data_status_flag)
              {
                any_block_read = true;
                int_BlockID_Status = 1;
                char temp_array[4] = {0};
                sprintf(temp_array, "%02s", (String)int_BlockID_Status);
                BlockIDs_Buffer[blockindex] = temp_array;
                BlockIDs_Buffer[blockindex] += "|";
                BlockIDs_Buffer[blockindex] += BlockID_No;
              }
              else
              {
                // breakLoop = 1;
                break;
              }
            // }
          }
          else
          {
            break;
          }
        // } while (Maxwell_loopCount < 2); // Version 3
      }                  // if (!int_BlockID_Status)

      // if (breakLoop == 1)
      // {
      //   breakLoop = 0;
      //   break;
      // }
    }

    if (any_block_read) // Version 5.2
    {
      seriallogger_string("UPDATEING STATUS FILE: " + temp_fileName);
      WriteIntoBlockIDFile(fileName, BlockIDs_Buffer, fileline_count);
      any_block_read = false;
    }

    file = dir.openNextFile();
  }
}

void RTC()
{
  // put your main code here, to run repeatedly:
  timeNow = millis() / 1000; // the number of milliseconds that have passed since boot

  g_seconds = ((timeNow - timeLast)); // the number of g_seconds that have passed since the last time 60 g_seconds was reached.

  if (g_seconds >= 60)
  {
    timeLast = timeNow;
    g_minutes = g_minutes + 1;
  }

  // if one minute has passed, start counting milliseconds from zero again and add one minute to the clock.

  if (g_minutes >= 60)
  {
    g_minutes = 0;
    g_hours = g_hours + 1;
  }

  // if one hour has passed, start counting g_minutes from zero and add one hour to the clock

  if (g_hours == 24)
  {
    g_hours = 0;
    g_days = g_days + 1;
  }

  // if 24 g_hours have passed , add one g_day

  if (g_hours == (24 - g_startingHour) && g_correctedToday == 0)
  {
    delay(g_dailyErrorFast * 1000);
    g_seconds = g_seconds + g_dailyErrorBehind;
    g_correctedToday = 1;
  }

  // every time 24 g_hours have passed since the initial starting time and it has not been reset this g_day before, add milliseconds or delay the progran with some milliseconds.
  // Change these varialbes according to the error of your board.
  //  The only way to find out how far off your boards internal clock is, is by uploading this sketch at exactly the same time as the real time, letting it run for a few g_days
  //  and then determine how many g_seconds slow/fast your boards internal clock is on a daily average. (24 g_hours).

  if (g_hours == 24 - g_startingHour + 2)
  {
    g_correctedToday = 0;
  }
 
  
  // let the sketch know that a new g_day has started for what concerns correction, if this line was not here the arduiono
  //  would continue to correct for an entire hour that is 24 - g_startingHour.
}

void handlelogs()
{
  File readpushfile = LittleFS.open("/loginfo1.txt", "r");

  if (!readpushfile)
  {
    server.send(200, "text/html", "5055534846494C45204E4F542050524553454E54");
    return;
  }
  else
  {
    size_t fsizeSent = server.streamFile(readpushfile, "text/plain");
    readpushfile.close();
  }
}

void handlefiledata()
{

  if (server.hasArg("filename"))
  {
    String filename_l = server.arg("filename");

    File c2 = LittleFS.open("/OBSC/" + filename_l, "r");
    if (c2)
    {
      String readbuf;
      readbuf = c2.readString();
      c2.close();
      if (isSpace(readbuf[0]))
      { // tests if myChar is a white-space character
        // Serial2.print("there is space");
      }
      if (readbuf != 0)
      {
        server.send(200, "text/html", readbuf);
      }
      else
      {
        server.send(200, "text/html", "File is Empty");
      }
    } // end of c2 check
    else
    {
      server.send(200, "text/html", "Unable to Open File/No such file");
    }
  }
  else
  {
    server.send(200, "text/html", "Argument missing");
  }
}

void handlefiledata1()
{

  if (server.hasArg("filename"))
  {
    String filename_l = server.arg("filename");

    File c2 = LittleFS.open("/BData/" + filename_l, "r");
    if (c2)
    {
      String readbuf;
      readbuf = c2.readString();
      c2.close();
      if (isSpace(readbuf[0]))
      { // tests if myChar is a white-space character
        // Serial2.print("there is space");
      }
      if (readbuf != 0)
      {
        server.send(200, "text/html", readbuf);
      }
      else
      {
        server.send(200, "text/html", "File is Empty");
      }
    } // end of c2 check
    else
    {
      server.send(200, "text/html", "Unable to Open File/No such file");
    }
  }
  else
  {
    server.send(200, "text/html", "Argument missing");
  }
}

void handlefilelist()
{

  String file_list;
  int fsize = 0;
  File dir = LittleFS.open("/OBSC");

  File file = dir.openNextFile();
  while (file)
  {
    file_list += (String)file.name() + ",";
    fsize += dir.size();

    file = dir.openNextFile();
  }
  if (file_list != 0)
  {
    server.send(200, "text/html", file_list);
  }
  else
  {
    server.send(200, "text/html", "No file exist");
  }
  seriallogger_string((String)fsize);
}

void handlefilelist1()
{

  String file_list;
  int fsize = 0;
  File dir = LittleFS.open("/BData");

  File file = dir.openNextFile();
  while (file)
  {
    file_list += (String)file.name() + ",";
    fsize += dir.size();

    file = dir.openNextFile();
  }
  if (file_list != 0)
  {
    server.send(200, "text/html", file_list);
  }
  else
  {
    server.send(200, "text/html", "No file exist");
  }
  seriallogger_string((String)fsize);
}

void handleblockstatusfilelist()
{

  String file_list;
  int fsize = 0;
  File dir = LittleFS.open("/blkstatus");
  File file = dir.openNextFile();
  while (file)
  {
    file_list += (String)file.name() + ",";
    fsize += dir.size();

    file = dir.openNextFile();
  }
  if (file_list != 0)
  {
    server.send(200, "text/html", file_list);
  }
  else
  {
    server.send(200, "text/html", "No file exist");
  }
}

void handledeletemeterdata()
{

  if (server.hasArg("filename"))
  {
    String filename_l = server.arg("filename");

    delay(3000);

    bool is_file_delete_success = LittleFS.remove("/OBSC/" + filename_l);
    if (is_file_delete_success == true)
    {
      server.send(200, "text/html", "File Delete successful");
    }
    else
    {
      server.send(200, "text/html", "No such file exists/Unable to Delete");
    }
  }
  else
  {
    server.send(200, "text/html", "Argument missing");
  }
}

void handledeletefile()
{
  if (server.hasArg("filename"))
  {
    String filename_l = server.arg("filename");

    seriallogger_string(filename_l);

    delay(3000);

    bool is_file_delete_success = LittleFS.remove(filename_l);
    if (is_file_delete_success == true)
    {
      server.send(200, "text/html", "File Delete successful");
    }
    else
    {
      server.send(200, "text/html", "No such file exists/Unable to Delete");
    }
  }
  else
  {
    server.send(200, "text/html", "Argument missing");
  }
}

void handleNonmeterfiledata()
{
  if (server.hasArg("filename"))
  {
    String filename = server.arg("filename");
    File c2 = LittleFS.open(filename, "r");
    if (c2)
    {
      String readbuf;
      readbuf = c2.readString();
      c2.close();
      if (isSpace(readbuf[0]))
      { // tests if myChar is a white-space character
        // Serial2.print("there is space");
      }
      if (readbuf != 0)
      {
        server.send(200, "text/html", readbuf);
      }
      else
      {
        server.send(200, "text/html", "File is Empty");
      }
    } // end of c2 check
    else
    {
      server.send(200, "text/html", "Unable to Open File/No such file");
    }
  }
  else
  {
    server.send(200, "text/html", "Argument missing");
  }
}

void handleformatnode()
{
  seriallogger_string("FORMATING NODE");
  server.send(200, "text/html", "FORMATING NODE");
  LittleFS.format();
  delay(20000);
  ESP.restart();
}

void handleavailablememory()
{
  server.send(200, "text/html", String(LittleFS.totalBytes() - LittleFS.usedBytes()));
}
void handlerestartnode()
{
  seriallogger_string("RESTARTING NODE");
  server.send(200, "text/html", "RESTARTING NODE");
  delay(2000);
  ESP.restart();
}
void handlefirmwareversion()
{
  server.send(200, "text/html", (String)SOFTWARE_VERSION);
}
// Version 5

void handlerelayop()
{
  if (server.hasArg("status"))
  {
    String relay_position = server.arg("status");
    if (relay_position.equals("0"))
    {
      digitalWrite(RELAY_OFF, HIGH);
      delay(1000);
      digitalWrite(RELAY_OFF, LOW);
      delay(1000);
      server.send(200, "text/html", "52454C4159204953204F4646");
      WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "0");
      return;
    }
    else if (relay_position.equals("1"))
    {
      digitalWrite(RELAY_ON, HIGH);
      delay(1000);
      digitalWrite(RELAY_ON, LOW);
      delay(1000);
      server.send(200, "text/html", "52454C4159204953204F4E");
      WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "1");
      return;
    }
    else
    {
      server.send(404, "text/html", "52454C4159204953204F4E");
      WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "RELAY STATUS NOT FOUND");
      return;
    }
  }
}

void seriallogger(unsigned char loginfo)
{
  File readfile = LittleFS.open("/loginfo1.txt", "a");
  ////seriallogger_string("logging data");
  ////Serial2.print(loginfo);

  if (readfile)
  {
    /*readfile.print(loginfo);
    readfile.print(' ');*/
    if (loginfo == '\r' || loginfo == '\n')
      readfile.println();
    else
    {
      readfile.print(loginfo, HEX);
      readfile.print(' ');
    }

    //    //Serial2.print("file reading ");
  }
  readfile.close();
}

void seriallogger_string(String loginfo)
{
  File readfile = LittleFS.open("/loginfo1.txt", "a");
  // Serial2.println();
  if (readfile)
  {
    if (METER_DEBUG == TRUE)
    {
      // Serial2.println();
      Serial2.println(loginfo);
    }
    readfile.println(loginfo);
  }
  readfile.close();
}

void memsetbuffer(char *buffer_name, uint32_t len)
{
  uint32_t i = 0;

  for (i = 0; i < len; i++)
  {
    buffer_name[i] = 0;
  }
}

void CreateBlockIDFIle(String FileName)
{
  // seriallogger_string("\r\nTOP\r\n");
  if (!LittleFS.exists(FileName))
  {
    // seriallogger_string("INSIDE");
    // seriallogger_string("\r\nCREATING BLOCK STATUS LOG FILE NOW\r\n");
    seriallogger_string("CREATING BLOCK STATUS LOG FILE NOW");

    // LittleFS.setTimeCallback(myTimeCb);//Version 5.2

    WriteIntoBlockIDFile(FileName, BlockIDs, (sizeof(BlockIDs) / sizeof(BlockIDs[0])));
    // ReadFromFile(FileName);
    // for(int i = 0; i < (sizeof(BlockIDs)/12); i++)
    //{
    //   seriallogger_string(BlockIDs_Buffer[i]);
    // }
  }
}

void CheckForMeterChange(String arg_MSN)
{
  String p;
  String fs_MSN_path = "";
  String BlockIDsFileName = "";
  fs_MSN_path = "/MeterSlNo";
  fs_MSN_path += "/";
  fs_MSN_path += "MSN.txt";

  arg_MSN.trim();

  String FromFileMSN = ReadMSNFromFile(fs_MSN_path);
  FromFileMSN.trim();

  if (FromFileMSN.equals(arg_MSN))
  {
    seriallogger_string("NO METER CHANGE");
  }
  else if (FromFileMSN == "NILL")
  {
    WritePostDataIntoBlockIDFile(fs_MSN_path, arg_MSN);
    seriallogger_string("MSN FILE CREATED");
    WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt","1");
    WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt","1");
    WritePostDataIntoBlockIDFile("/StatusFlag/OBIS.txt","1");
  }
  else
  {
    // REMOVE ALL OLD FILES IN THE MEMORY WHEN METER GOT CHANGED
    seriallogger_string("NEW METER DETECTED");
    LittleFS.format();
    delay(20000);
    ESP.restart();
  }
}

/*READ MSN FROM FILE*/
String ReadMSNFromFile(String MSNFileName)
{
  String MSN = "";
  // File file2 = LittleFS.open(ReadFileName);
  seriallogger_string("file name"+MSNFileName);
  File file2 = LittleFS.open(MSNFileName, "r");

  if (!file2)
  {
    // seriallogger_string("Failed to open file for reading");
    seriallogger_string("Failed to open file for reading");
    return "NILL";
  }

  // seriallogger_string(ReadFileName);

  ////seriallogger_string("File Content: ");

  char bufferc[16];
  while (file2.available())
  {
    // Serial2.write(file2.read());//Original

    /*int a = file2.readBytesUntil('\n', bufferc, sizeof(bufferc));
    bufferc[a] = 0;
    MSN = (String)bufferc;*/

    MSN = file2.readString();
  }
  ////seriallogger_string();

  ////seriallogger_string();
  file2.close();

  return MSN;
}
/*READ MSN FROM FILE*/

void DeleteFilesInDrectory(String DirectoryName)
{
  String temp_fileName = "";
  String fileName = "";
  int char_index = 0;
  // Dir dir = LittleFS.openDir(DirectoryName);
  File dir = LittleFS.open(DirectoryName);

  File file = dir.openNextFile();
  while (file)
  {
    temp_fileName += (String)file.name() + ",";
    file = dir.openNextFile();
  }
  seriallogger_string(temp_fileName);
  // file.close();

  while (getValue(temp_fileName, ',', char_index) != "")
  {
    String f_name = getValue(temp_fileName, ',', char_index++);

    if (f_name.endsWith(","))
      f_name = f_name.substring(0, f_name.length() - 1);

    String delete_file_path = DirectoryName + "/" + f_name;
    seriallogger_string("DELETEING: " + delete_file_path);
    deleteFile(LittleFS, delete_file_path);
  }
}

// CHECK LOG FILE SIZE
void CheckLogFileSize()
{
  int filesize = {0};
  File file = LittleFS.open("/loginfo1.txt", "r");
  filesize = file.size();
  file.close();
  // seriallogger_string((String)filesize);
  if (filesize >= 10000) // IF FILE SIZE IS GREATER THAN 10KB, THEN DELETE THE FILE
  {
    LittleFS.remove("/loginfo1.txt");
    seriallogger_string("LOG FILE DELETED");
  }
}

// Check MeterReadingData Files Total Size
void CheckMeterDataFilesSize()
{
  String file_list;
  int fsize = 0;
  // Dir dir = LittleFS.openDir("/OBSC");
  File dir = LittleFS.open("/OBSC");

  while (dir.openNextFile())
  {
    fsize += dir.size();
  }

  if (fsize >= 1000000) // IF TOTAL FILE SIZE OF METER DATA IS GREATER THAN 1MB(10,00,000 Bytes in Appox.), CLEAR ALL FILES.
  {
    DeleteFilesInDrectory("/OBSC");
    seriallogger_string("METER DATA MEMORY IF FULL, CLEARING OLD DATA.");
  }
}

void handleresumereading()
{
  if (server.hasArg("status"))
  {
    String resume_status = server.arg("status");
    if (resume_status.equals("resume"))
    {
      resume_reading_instant = 1;

      server.send(200, "text/html", "RESUMING METER READING");
      return;
    }
    else
    {
      server.send(404, "text/html", "FAILED");
      return;
    }
  }
}

void handleresumereadingload()
{
  if (server.hasArg("status"))
  {
    String resume_status = server.arg("status");
    if (resume_status.equals("resume"))
    {
      resume_reading_load = 1;

      server.send(200, "text/html", "RESUMING METER LOAD READING");
      return;
    }
    else
    {
      server.send(404, "text/html", "FAILED");
      return;
    }
  }
}

void handleresumereadinggsm()
{
  if (server.hasArg("status"))
  {
    String resume_status = server.arg("status");
    if (resume_status.equals("resume"))
    {
      resume_reading_gsm = 1;

      server.send(200, "text/html", "RESUMING METER LOAD READING");
      return;
    }
    else
    {
      server.send(404, "text/html", "FAILED");
      return;
    }
  }
}

void handlemeterslno()
{
  String MSN = ReadMSNFromFile("/MeterSlNo/MSN.txt");
  if (MSN.length() == 0)
  {
    server.send(200, "text/html", "4D534E204E4F5420464F554E44");
    return;
  }
  else
  {
    server.send(200, "text/html", MSN);
    return;
  }
}

void handlerelaystatus()
{
  String MSN = ReadMSNFromFile("/RelayStatus/status.txt"); // READING REALY STATUS FROM FILE
  if (MSN.length() == 0)
  {
    server.send(200, "text/html", "RELAY STATUS NOT FOUND");
    return;
  }
  else
  {
    server.send(200, "text/html", MSN);
    return;
  }
}

int temp_LoadReqFrame(char fromDateTime[], char ToDateTime[])
{
  // char LoadREQframeptr[10][MAX_SIZE] = {0};
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  char MeterDataType = LOAD_PROFILE_DATA;
  int mx_res_count = 0;
  int temp_buff_size = 0;
  global_frame = "";
  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  if (METER_DEBUG == TRUE)
  {
    // Serial2.println();
    Serial2.println("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
  }
  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  SerialRead(arrindex, ResByteCount);
  // seriallogger_string("READ SNRM");

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
  }

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  // 04-04-2022
  GetSequenceNumber(0);

  DateTimeRange(Fromdate, Todate, fromDateTime, ToDateTime);

  // for (i = 0; i < 4; i++)
  // {
    MeterCommandFrame(Fromdate, Todate, MeterDataType);
    // 04-04-2022
    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);

    ResByteCount = 0;

    load_array[0] = arrindex;
    
    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("Req : ");
      Serial2.print(arrindex);
      Serial2.print(" ");
      for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][i], HEX);
        Serial2.print(" ");
      }
    }//end if (METER_DEBUG == TRUE)
    SerialRead(arrindex, ResByteCount);

    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }

    if(ResponseBuffer[arrindex][11] != 0xC4)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }
    
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

    for (int filedata = 0; filedata < (temp_buff_size + 2); filedata++)
    {
      global_frame = global_frame + String(ResponseBuffer[arrindex][filedata], HEX);
      global_frame = global_frame + " ";
    }
    global_frame.trim();

    while ((ResponseBuffer[arrindex][1] == 0xA8))
    {
      if(mx_res_count >= COUNT_LP)
      {
          seriallogger_string("While count break : " +String(mx_res_count));
          break;
      }

      // seriallogger_string("SUPERVISORY RESPONSE");
      FrameType = SUPERVISORY_FRAME;
      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(++arrindex, LoadREQframeptr);

      ResByteCount = 0;

      if (METER_DEBUG == TRUE)
      {
        Serial2.println();
        Serial2.print("Req : ");
        Serial2.print(arrindex);
        Serial2.print(" ");
        for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
        {
          Serial2.print(LoadREQframeptr[arrindex][i], HEX);
          Serial2.print(" ");
        }
      }
      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      SerialRead(arrindex, ResByteCount);

      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");
        return 0;
      }
      //////////////////////////////////////////////////////////////
      global_frame = global_frame + "_";

      temp_buff_size = 0;

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

      for (int c = 0; c < temp_buff_size + 2; c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }

      global_frame.trim();
      ////////////////////////////////////////////////////
      seriallogger_string("While count : "+String(mx_res_count));
      mx_res_count++;
    }
    /*****************************************************************************************/
  // }

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;
  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();
  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
  }
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;

  /// ChoppedByteCount = ChopLoadMeterResponse(ResponseBuffer, (arrindex + 1));
  /// return ChoppedByteCount;
  return 1;
}

void Set_Default_RTC()
{
  g_year = 2022;
  g_month = 01;
  g_day = 06;
  g_hours = 10;
  g_minutes = 40;
  g_seconds = 00;
  rtc.setTime(00, 40, 10, 06, 01, 2022);
  rtc.setTime();
}
bool CheckForInstDataStatus()
{
  char temp[5] = {0};
  String infile_status = ReadMSNFromFile("/InstDataStatus.txt");
  if (infile_status == "NILL")
  {
    seriallogger_string("INST DATA FILE NOT EXISTS");
    return false;
  }

  String current_status = "";
  // sprintf(temp, "%02s", (String)rtc.getHour());

  if (rtc.getAmPm(true).equals("pm") && rtc.getHour() != 12)
    sprintf(temp, "%02s", (String)(rtc.getHour() + 12));
  else
    sprintf(temp, "%02s", (String)(rtc.getHour()));

  current_status += temp;
  current_status += "_";
  sprintf(temp, "%02s", (String)rtc.getDay());
  current_status += temp;
  sprintf(temp, "%02s", (String)(rtc.getMonth() + 1));
  current_status += temp;
  sprintf(temp, "%04s", (String)rtc.getYear());
  current_status += temp;
  current_status += "_";

  seriallogger_string("infile_status: " + infile_status);
  seriallogger_string("current_status: " + current_status);

  if ((infile_status.indexOf(current_status) >= 0) && (infile_status.indexOf("_I.txt") >= 0)) // IF FILE NAME MATCHES
  {
    seriallogger_string("INST DATA FLAG ALREADY READ");
    return true;
  }
  else
  {
    seriallogger_string("INST DATA FLAG NOT SET");
    return false;
  }
}

/*WRITE POST DATA INTO BLOCK ID FILE*/ // 30-03-2022
void WriteIntoFile(String WriteFileName, String FileContent)
{
  if (FileContent.length() <= 0)
    return;

  File file = LittleFS.open(WriteFileName, "w");

  ////seriallogger_string(WriteFileName);
  if (!file)
  {
    seriallogger_string("There was an error opening the file for writing");
    return;
  }

  if (file.println(FileContent))
  {
    seriallogger_string("File was written");
  }
  else
  {
    seriallogger_string("File write failed");
  }
  file.close();
}
/*WRITE POST DATA INTO BLOCK ID FILE*/

// Version 3 additions START
void handlecommandtonode()
{
  if (server.hasArg("command"))
  {
    String command_string = server.arg("command");

    if (command_string.length() > 0)
    {
      WriteIntoFile("/CommandDirectory/Command.txt", command_string);
      seriallogger_string(command_string);
      seriallogger_string("------------------");

      command_available = 1;
      server.send(200, "text/html", "52454C4159204953204F4646");
      return;
    }
    else
    {
      server.send(404, "text/html", "52454C4159204953204F4E");
      return;
    }
  }
}

void CheckAndExecuteCommandsToNodes(String command_to_node)
{
  String IMEI = "";
  String NodeID = "";
  seriallogger_string(command_to_node);
  SERIAL_MST("command is " + command_to_node);

  String commandtype = getValue(command_to_node, '|', 0);
  seriallogger_string("commandtype: " + commandtype);
  if(commandtype == "I")
  {
    IMEI = getValue(command_to_node, '|', 1);
    IMEI.trim();
    Serial2.println("IMEI: " + IMEI);
  }
  else
  {

    NodeID = getValue(command_to_node, '|', 1);
    Serial2.println("NodeID: " + NodeID);
  }
  String CommandID = getValue(command_to_node, '|', 2);
  Serial2.println("CommandID: " + CommandID);

  String CommandData = getValue(command_to_node, '|', 3);
  Serial2.println("CommandData: " + CommandData);

  String CommandIndex = getValue(command_to_node, '|', 4);
  CommandIndex.trim();
  Serial2.println("CommandIndex: " + CommandIndex);

  String command_ack_file_name = "";
  char temp[5] = {0};
  command_ack_file_name = "/OBSC/C_" + CommandIndex + ".txt";
  Serial2.println("file: " + command_ack_file_name);
  global_NodeID.trim();
  NodeID.trim();
  String imeinumber = ReadMSNFromFile("/IMEI");
  imeinumber.trim();
  String command_ack_string = "$" + global_NodeID + "_" + (String)PhaseType + "_" + "C_" + CommandIndex + "$";
  Serial2.println("in reading: " +NodeID + global_NodeID+imeinumber+IMEI);
  if((commandtype == "I" && IMEI == imeinumber )||(commandtype == "N" && NodeID == global_NodeID))
  {
  Serial2.println("hii im in");  
  int char_index = 0;
  int blk_index = 0;
  String BlockIDsFileName = "";
  String Blocks[24] = {"0"};
  String Multi_BlockIDsFileName = "";
  String firstentry = "";
  String lastentry = "";
  String data = "";
  switch(CommandID.toInt())
  {
      case 0:
                if (CommandData.equals("0")) // Relay Operation
                {
                  digitalWrite(RELAY_OFF, HIGH);
                  delay(1000);
                  digitalWrite(RELAY_OFF, LOW);
                  delay(1000);
                  WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "0");
                  WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                }
                else if (CommandData.equals("1"))
                {
                  digitalWrite(RELAY_ON, HIGH);
                  delay(1000);
                  digitalWrite(RELAY_ON, LOW);
                  delay(1000);
                  WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "1");
                  WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                }
                break;

      case 1:
                // Full Day Block Reading
                Serial2.println("in full day reading");

                BlockIDsFileName = "/blkstatus/";
                BlockIDsFileName += CommandData;
                BlockIDsFileName += ".txt";
                CreateBlockIDFIle(BlockIDsFileName);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);  
                break; 
         
      case 2:   // Read missing blocks only
                Multi_BlockIDsFileName = "/blkstatus/";
                Multi_BlockIDsFileName += getValue(CommandData, '_', char_index++);
                Multi_BlockIDsFileName += "_C";
                Multi_BlockIDsFileName += ".txt";
                seriallogger_string(Multi_BlockIDsFileName);
                while (getValue(CommandData, '_', char_index) != "")
                {
                  Blocks[blk_index++] = getValue(CommandData, '_', char_index++) + "|" + getValue(CommandData, '_', char_index++);
                  seriallogger_string(Blocks[blk_index - 1]);
                }

                WriteIntoBlockIDFile(Multi_BlockIDsFileName, Blocks, blk_index);

                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                // Version 5.2

      case 3 :  //Write Threshold kWh into File
                WritePostDataIntoBlockIDFile("/kWhThreshold/kWhValue.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;

      case 4 :  // Read Billing Profile
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Bill.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;
      
      case 5 :  // Read Scalar 
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;

      case 6 :  // Read events
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string); 
                break;

      case 7 :  //  Read OBIS
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/OBIS.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;


      case 8 :  // Format node
                CommandData.trim();
                FormatNode();         
                break;
      
      case 9 :  // Read Instantaneous
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Instant.txt", CommandData);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;

      case 10 :  // Read Billing Profile
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/BillOnDemand.txt", "1");
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                firstentry = getValue(CommandData, '_', 0);
                lastentry = getValue(CommandData, '_', 1);
                WritePostDataIntoBlockIDFile("/firstentry.txt", firstentry);
                WritePostDataIntoBlockIDFile("/lastentry.txt", lastentry);
                break;    

     case 11 :  // Read Billing Profile
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Load.txt", "1");
                WritePostDataIntoBlockIDFile("/ReadFulldayLoad.txt", CommandData);
                data = ReadMSNFromFile("/ReadFulldayLoad.txt");
                Serial2.println("data : "+data);
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
                break;   

     case 12 :  // Read Billing Profile
                CommandData.trim();
                WritePostDataIntoBlockIDFile("/StatusFlag/Bill.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/OBIS.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/Instant.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/BillOnDemand.txt", "0");
                WritePostDataIntoBlockIDFile("/StatusFlag/Load.txt", "0");
                WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);

                break;   
   }
  }
  command_available = 1;
}

String getValue(String data, char separator, int index)
{
  int found = 0;
  int strIndex[] = {0, -1};
  int maxIndex = data.length() - 1;

  for (int i = 0; i <= maxIndex && found <= index; i++)
  {
    if (data.charAt(i) == separator || i == maxIndex)
    {
      found++;
      strIndex[0] = strIndex[1] + 1;
      strIndex[1] = (i == maxIndex) ? i + 1 : i;
    }
  }
  return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}

float ParseMeterkWh(byte kWhValue[], byte kWhScalar[])
{
  int index = 0;
  unsigned long ddoublelongvalue = 0;
  int scalar = 0;
  unsigned int unit = 0;
  float kWh_finalvalue = 0, kWh_floatvalue = 0;
  ;
  if (kWhValue[index] == DT_DOUBLE_LONG || kWhValue[index] == DT_DOUBLE_LONG_UNSIGNED)
  {
    index++;
    while (index < (sizeof(int) + 1))
    {
      ddoublelongvalue = (ddoublelongvalue << 8) | kWhValue[index++];
    }
    kWh_floatvalue = (float)ddoublelongvalue;
  }

  index = 2;
  if (kWhScalar[index] == DT_INTEGER)
  {
    index++;
    scalar = kWhScalar[index];
    if (scalar > 127)
      scalar = scalar - 256;

    index += 2;
    unit = kWhScalar[index];
    switch (unit)
    {
    case Active_Energy:
    case Active_Power:
    case Apparent_Energy:
    case Apparent_Power:
    case Reactive_Energy:
    case Reactive_Power:
      scalar -= 3;
      break;
    default:
      break;
    }
  }
  kWh_finalvalue = (float)(kWh_floatvalue * pow(10, scalar));
  return kWh_finalvalue;
}

bool CheckForFileExistence(String FileName)
{
  if (LittleFS.exists(FileName))
  {
    return true;
  }
  else
  {
    return false;
  }
}

void ExecuteIndividualBlockRead()
{
  bool blockreadStatus = false;
  String CommandData = ReadMSNFromFile("/IndividualBlock.txt");

  String CommandIndex = getValue(CommandData, '_', 0); // CommandIndex_dd-mm-yyyy_00_12

  String BlockDate = getValue(CommandData, '_', 1); // CommandIndex_dd-mm-yyyy_00_12
  seriallogger_string("BlockDate: " + BlockDate);

  String block_Day = getValue(BlockDate, '-', 0);
  String block_Month = getValue(BlockDate, '-', 1);
  String block_Year = getValue(BlockDate, '-', 2);
  seriallogger_string(block_Day + "-" + block_Month + "-" + block_Year);

  String BlockStatus = getValue(CommandData, '_', 2); // CommandIndex_dd-mm-yyyy_00_12
  seriallogger_string("BlockStatus: " + BlockStatus);
  String BlockID = getValue(CommandData, '_', 3); // CommandIndex_dd-mm-yyyy_00_12
  seriallogger_string("BlockID: " + BlockID);

  if (BlockStatus.toInt() == 0)
  {
    String command_ack_file_name = "/OBSC/C_" + CommandIndex + ".txt";
    String command_ack_string = "$" + global_NodeID + "_" + (String)PhaseType + "_" + "C_" + CommandIndex + "$";

    blockreadStatus = ReadLoadProfileData(BlockID.toInt(), 0, block_Day.toInt(), block_Month.toInt(), block_Year.toInt());

    // if (METER_MAKE == LT)
    blockreadStatus = ReadLoadProfileData(BlockID.toInt(), 30, block_Day.toInt(), block_Month.toInt(), block_Year.toInt());

    if (blockreadStatus)
    {
      WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);
      WritePostDataIntoBlockIDFile("/IndividualBlock.txt", (CommandIndex + "_" + BlockDate + "_" + "01_" + BlockID));
    }
  }
}

// Version 5.1
void ExecuteMultipleBlockRead()
{
  int _index = 0;
  String str = "";
  bool blockreadStatus = false;
  String CommandData = ReadMSNFromFile("/IndividualBlock.txt");

  String CommandIndex = getValue(CommandData, '_', _index++); // CommandIndex_dd-mm-yyyy_00_12

  String BlockDate = getValue(CommandData, '_', _index++); // CommandIndex_dd-mm-yyyy_00_12
  seriallogger_string("BlockDate: " + BlockDate);

  String block_Day = getValue(BlockDate, '-', 0);
  String block_Month = getValue(BlockDate, '-', 1);
  String block_Year = getValue(BlockDate, '-', 2);
  seriallogger_string(block_Day + "-" + block_Month + "-" + block_Year);

  String command_ack_file_name = "/OBSC/C_" + CommandIndex + ".txt";
  String command_ack_string = "$" + global_NodeID + "_" + (String)PhaseType + "_" + "C_" + CommandIndex + "$";

  str = CommandIndex + "_" + BlockDate + "_";
  while (getValue(CommandData, '_', _index) != "")
  {
    String BlockStatus = getValue(CommandData, '_', _index++); // CommandIndex_dd-mm-yyyy_00_12
    seriallogger_string("BlockStatus: " + BlockStatus);
    String BlockID = getValue(CommandData, '_', _index++); // CommandIndex_dd-mm-yyyy_00_12
    seriallogger_string("BlockID: " + BlockID);

    // Load Read Function Will be called here
    if (BlockStatus.toInt() == 0)
    {
      blockreadStatus = ReadLoadProfileData(BlockID.toInt(), 0, block_Day.toInt(), block_Month.toInt(), block_Year.toInt());

      // if (METER_MAKE == LT)
      blockreadStatus = ReadLoadProfileData(BlockID.toInt(), 30, block_Day.toInt(), block_Month.toInt(), block_Year.toInt());
      if (blockreadStatus)
      {
        if (getValue(CommandData, '_', _index) == "")
          str += "01_" + BlockID;
        else
          str += "01_" + BlockID + "_";
      }
      else
      {
        if (getValue(CommandData, '_', _index) == "")
          str += "00_" + BlockID;
        else
          str += "00_" + BlockID + "_";
      }
    }
    else
    {
      if (getValue(CommandData, '_', _index) == "")
        str += BlockStatus + "_" + BlockID;
      else
        str += BlockStatus + "_" + BlockID + "_";
    }
    ObiscodeIndex = 0; // 06-07-2022 Re-Initialize ObiscodeIndex to start it from 0 for next block.
  }
  seriallogger_string(str);

  if (!LittleFS.exists(command_ack_file_name))
    WritePostDataIntoBlockIDFile(command_ack_file_name, command_ack_string);

  WritePostDataIntoBlockIDFile("/IndividualBlock.txt", str);
}
// Version 5.1

int GetDateDifference(String StartDate, String EndDate)
{
  int day1, mon1, year1, day2, mon2, year2;
  int day_diff, mon_diff, year_diff;

  day1 = getValue(StartDate, '-', 0).toInt();
  mon1 = getValue(StartDate, '-', 1).toInt();
  year1 = getValue(StartDate, '-', 2).toInt();

  day2 = getValue(EndDate, '-', 0).toInt();
  mon2 = getValue(EndDate, '-', 1).toInt();
  year2 = getValue(EndDate, '-', 2).toInt();

  if (day2 < day1)
  {
    // borrow g_days from february
    if (mon2 == 3)
    {
      //  check whether g_year is a leap g_year
      if ((year2 % 4 == 0 && year2 % 100 != 0) || (year2 % 400 == 0))
      {
        day2 += 29;
      }

      else
      {
        day2 += 28;
      }
    }

    // borrow g_days from April or June or September or November
    else if (mon2 == 5 || mon2 == 7 || mon2 == 10 || mon2 == 12)
    {
      day2 += 30;
    }

    // borrow g_days from Jan or Mar or May or July or Aug or Oct or Dec
    else
    {
      day2 += 31;
    }

    mon2 = mon2 - 1;
  }

  if (mon2 < mon1)
  {
    mon2 += 12;
    year2 -= 1;
  }

  day_diff = day2 - day1;
  mon_diff = mon2 - mon1;
  year_diff = year2 - year1;

  seriallogger_string("Difference: " + (String)day_diff);
  return day_diff;
}

// Check MeterReadingData Files Total Size
void CheckBlockStatusFilesSize()
{
  String file_name = "", current_date = "";
  // Dir dir = LittleFS.openDir("/blkstatus");
  File dir = LittleFS.open("/blkstatus");

  File file = dir.openNextFile();
  while (file)
  {
    // Version 5.2
    // File file = file1.openFile("r");
    // time_t cr = file.getLastWrite();
    // struct tm *tmstruct = localtime(&cr);
    // file_name = (String)tmstruct->tm_mday + "-" + ((String)tmstruct-> tm_mon + 1 ) + "-" + (String)((tmstruct->tm_year) + 1900) + ".txt"; // File Creation Date

    file_name = file.name();
    int index = file_name.indexOf('-');
    String prev_file_date = file_name.substring(0, index);

    String today_date = String(g_day);

    // file_name = file.name();
    seriallogger_string("FILE CREATED DATE: " + file_name);
    current_date = (String)g_day;
    current_date += "-";
    current_date += (String)g_month;
    current_date += "-";
    current_date += (String)g_year;
    current_date += ".txt";
    seriallogger_string("CURRENT DATE: " + current_date);

    // if (GetDateDifference(file_name, current_date) > 14)
    if ((prev_file_date != today_date) & (g_hours >= 8))
    {
      seriallogger_string("DELETING: " + file_name);
      file.close();
      bool filestatus = LittleFS.remove("/blkstatus/" + file_name);
      if (filestatus == 0)
      {
        seriallogger_string("file delete failed" + file_name);
      }
      // WritePostDataIntoBlockIDFile("/StatusFlag/Scalar.txt","1");
      // WritePostDataIntoBlockIDFile("/StatusFlag/Bill.txt","1");
      // WritePostDataIntoBlockIDFile("/StatusFlag/Event.txt","1");
    }

    file = dir.openNextFile();
  }
}

bool ValidateDateString(String DataFileName)
{
  String temp_data_string_for_validation = ReadMSNFromFile(DataFileName);

  if (temp_data_string_for_validation.startsWith("$"))
  {
    temp_data_string_for_validation.trim();
    if (temp_data_string_for_validation.endsWith("$"))
    {
      return true;
    }
    else
    {
      LittleFS.remove(DataFileName);
      return false;
    }
  }
  else
  {
    LittleFS.remove(DataFileName);
    return false;
  }
}
// Version 3 additions END

#if 0  // ESP8266
//Version 5.2
time_t myTimeCb() 
{
  //seriallogger_string("--- myTimeCb was called");
  //return tmConvert_t(g_year,g_month,g_day,g_hours,g_minutes,g_seconds);
  return tmConvert_t(rtc.getYear(),rtc.getMonth(),rtc.getDay(),rtc.getHour(),rtc.getMinute(),rtc.getSecond());
  //return tmConvert_t(2022,6,15,10,22,15);
}

time_t tmConvert_t(int YYYY, byte MM, byte DD, byte hh, byte mm, byte ss)
{
  tmElements_t tmSet;
  tmSet.Year = YYYY - 1970;
  tmSet.Month = MM;
  tmSet.Day = DD;
  tmSet.Hour = hh;
  tmSet.Minute = mm;
  tmSet.Second = ss;
  return makeTime(tmSet);
}
//Version 5.2
#endif // ESP8266

/////////////////////////FILE SYSTEM FUNCTIONS/////////////////////////////////

void createDir(fs::FS &fs, const char *path)
{
  if (fs.mkdir(path))
  {
    seriallogger_string("Dir created");
  }
  else
  {
    seriallogger_string("mkdir failed");
  }
}

void writeFile(String path, String message) ///
{
  SERIAL_MST("Writing file");
  SERIAL_MST(path);

  File file = LittleFS.open(path, "w");
  if (!file)
  {
    SERIAL_MST("Failed to open file for writing");
    return;
  }
  else
  {
    file.print(message);
    SERIAL_MST("File written");
  }

  file.close();
}

void deleteFile(fs::FS &fs, String path)
{
  SERIAL_MST(path);
  if (fs.remove(path))
  {
    SERIAL_MST("- file deleted");
  }

  else
  {
    SERIAL_MST("- delete failed");
  }
}

void appendFile(fs::FS &fs, String path, String message)
{
  File file = fs.open(path, FILE_APPEND);
  if (!file)
  {
   seriallogger_string("- failed to open file for appending");
    return;
  }
  else
  {
    if (message.length() == 0)
    {
      file.close();
      return;
    }
    else
    {
      message.trim();
      int size_of_array = message.length();
      char newarray[size_of_array] = {0};
      message.toCharArray(newarray, size_of_array + 1);
      delay(1000);
      file.print(newarray);
      seriallogger_string("file appended");
    }
  }
  file.close();
}

String readFile(fs::FS &fs, String path)
{
  String payload = "";

  SERIAL_MST("Reading file " + path);

  File file = fs.open(path);
  if (!file || file.isDirectory())
  {
    SERIAL_MST("Failed to open file for reading");
    return "error";
  }

  while (file.available())
  {
    payload = file.readString();
  }
  SERIAL_MST("File content : " + payload);

  SERIAL_MST("Length is : " + String(payload.length()));

  file.close();
  return payload;
}

int checkforDirectory(const char *dirname, uint8_t levels)
{
  File root = LittleFS.open(dirname);
  int ret = 0;
  if (!root)
  {
    seriallogger_string("- failed to open directory");
    return 0;
  }
  if (!root.isDirectory())
  {
    seriallogger_string(" - not a directory");
    ret = 0;
  }
  else
  {
    ret = 1;
  }

  root.close();
  return ret;
}

void handleclearfile(void)
{
  File fileclear;
  packetcnt = 0;

  fileclear = LittleFS.open("/update.bin", "w");

  if (!fileclear)
  {
    server.send(200, "text/html", "File creation failed");
    return;
  }
  else
  {
    server.send(200, "text/html", "FILE CLEARED");
    return;
  }
}

void handleupdatefirmware()
{
  SERIAL_MST("\nSearch for firmware..");

  File firmware = LittleFS.open("/gwotadownload.bin", "r");
  SERIAL_MST(String(firmware.size()));
  if (firmware)
  {
    SERIAL_MST("found!");
    SERIAL_MST("Try to update!");
    Update.onProgress(progressCallBack);
    Update.begin(firmware.size(), U_FLASH);

    Update.writeStream(firmware);

    if (Update.end())
    {
      SERIAL_MST("Update finished!");
    }
    else
    {
      SERIAL_MST("Update error!");
      SERIAL_MST(String(Update.getError()));
    }

    firmware.close();
    delay(2000);

    ESP.restart();
  }
  else
  {
    SERIAL_MST("not found!");
  }
}

void handlebinfile()
{

  int hexflag = 0;

  // OTA_Process_flag = 1;

  String filecontent;
  if (server.hasArg("data"))
  {
    filecontent = server.arg("data");
  }

  File writefile = LittleFS.open("/update.bin", "a+");

  if (!writefile)
  {
    server.send(200, "text/html", "SUCCESS");
    return;
  }

  else
  {

    int commandhexlen = (filecontent.length()) / 2 + 200;

    char *str = new char[commandhexlen];

    if (!str)
    {
      Serial1.println("FILEHEXRESPONSEBUFF ALLOCATION FAILED");
      server.send(200, "text/html", "FAILED");
      return;
    }

    hexflag = strtohex(filecontent, str);

    if (hexflag == 1)
    {
      packetcnt++;
      // Serial2.printf("Packet Cnt = %d len =%d \n\r ", packetcnt, filecontent.length());
      for (int len = 0; len < (filecontent.length()) / 2; len++)
      {
        writefile.print(str[len]);
      }
      delay(5);
      delete str;
      delay(5);
      server.send(200, "text/html", "PACKET SENT");
      return;
    }
    else
    {
      delay(5);
      delete str;
      delay(5);
      server.send(200, "text/html", "HEX FORMAT WRONG");
      return;
    }
  }
  // Serial2.println(writefile.size());
  writefile.close();

  server.send(200, "text/html", "success");
}

void progressCallBack(size_t currSize, size_t totalSize)
{
  SERIAL_MST("CALLBACK:  Update process at " + String(currSize) + " of " + String(totalSize) + " bytes...");
}

int strtohex(String strhex, char *hexresponsebuff)
{
  int l = strhex.length();
  int i = 0;
  char temp1 = 0, temp2 = 0;

  for (int k = 0; k < l / 2; k++)
  {
    if (strhex[i] == 'A' || strhex[i] == 'a')
    {
      temp1 = 10;
      i++;
    }
    else if (strhex[i] == 'B' || strhex[i] == 'b')
    {
      temp1 = 11;
      i++;
    }
    else if (strhex[i] == 'C' || strhex[i] == 'c')
    {
      temp1 = 12;
      i++;
    }
    else if (strhex[i] == 'D' || strhex[i] == 'd')
    {
      temp1 = 13;
      i++;
    }
    else if (strhex[i] == 'E' || strhex[i] == 'e')
    {
      temp1 = 14;
      i++;
    }
    else if (strhex[i] == 'F' || strhex[i] == 'f')
    {
      temp1 = 15;
      i++;
    }
    else
    {
      if (is_digit(strhex[i]) == 1)
      {
        temp1 = strhex[i] - 48;
        i++;
      }
      else
      {
        return 0;
      }
    }
    if (strhex[i] == 'A' || strhex[i] == 'a')
    {
      temp2 = 10;
      i++;
    }
    else if (strhex[i] == 'B' || strhex[i] == 'b')
    {
      temp2 = 11;
      i++;
    }
    else if (strhex[i] == 'C' || strhex[i] == 'c')
    {
      temp2 = 12;
      i++;
    }
    else if (strhex[i] == 'D' || strhex[i] == 'd')
    {
      temp2 = 13;
      i++;
    }
    else if (strhex[i] == 'E' || strhex[i] == 'e')
    {
      temp2 = 14;
      i++;
    }
    else if (strhex[i] == 'F' || strhex[i] == 'f')
    {
      temp2 = 15;
      i++;
    }
    else
    {
      if (is_digit(strhex[i]) == 1)
      {
        temp2 = strhex[i] - 48;
        i++;
      }
      else
      {
        // Serial2.printf("i=%d\n",i);
        return 0;
      }
    }

    hexresponsebuff[k] = ((temp1 << 4) | temp2);
  }
  return 1;
}

int is_digit(char s)
{
  char i = s - 48;
  if (i >= 0 && i <= 9)
  {
    return 1;
  }
  return 0;
}

/////////////////////////FILE SYSTEM FUNCTIONS/////////////////////////////////

//////////////////////////////////4G/////////////////////////////////////
/////////////////////////////////////////////////////////
// void createDir(fs::FS &fs, const char *path)
// {
//  if (fs.mkdir(path))
//  {
//    SERIAL_MST("Dir created");
//  }
//  else
//  {
//    SERIAL_MST("MKDIR failed");
//  }
// }

// void writeFile(String path, String message)//4GGGGGGGGGGGGGGGGGGGg part
// {
//  SERIAL_MST("Writing file " + path);
//  File file = LittleFS.open(path, "w");
//  if (!file)
//  {
//    SERIAL_MST("Failed to open file for writing");
//    return;
//  }
//  else
//  {
//    file.print(message);
//    SERIAL_MST("File written\n");
//  }
//  file.close();
// }

// void deleteFile(fs::FS &fs, String path)//4GGGGGGGGGGGGGGGGGGGGGgg
// {
//  if (fs.remove(path))
//  {
//    SERIAL_MST("File delete successfull\n");
//  }
//  else
//  {
//    SERIAL_MST("File delete failed as " + path + " file is not present");
//  }
// }

// void appendFile(fs::FS &fs, String path, String message)
// {
//  File file = fs.open(path, FILE_APPEND);
//  if (!file)
//  {
//    SERIAL_MST("Failed to open file for appending");
//    return;
//  }
//  else
//  {
//    if (message.length() == 0)
//    {
//      file.close();
//      return;
//    }
//    else
//    {
//      message.trim();
//      int size_of_array = message.length();
//      char newarray[size_of_array] = {0};
//      message.toCharArray(newarray, size_of_array + 1);
//      delay(1000);
//      file.print(newarray);
//      SERIAL_MST("Message Appended");
//    }
//  }
//  file.close();
// }

void appendFile_new(fs::FS &fs, String path, String message)
{
  SERIAL_MST("Appending to file: " + path);

  File file = fs.open(path, FILE_APPEND);
  if (!file)
  {
    return;
  }
  else if (message.length() != 0)
  {
    file.print(message);
  }
  file.close();
}


//////////////////////////CHECKDIRECTORYANDFILESIZE////////////////////////////////

// int checkforDirectory(const char *dirname, uint8_t levels)
// {
//  File root = LittleFS.open(dirname);
//  int ret = 0;
//  if (!root)
//  {
//    SERIAL_MST("Failed to open directory");
//    return 0;
//  }
//  if (!root.isDirectory())
//  {
//    SERIAL_MST("Not a directory");
//    ret = 0;
//  }
//  else
//  {
//    ret = 1;
//  }
//  root.close();
//  return ret;
// }

int checkforFiles(fs::FS &fs, const char *dirname, uint8_t levels,String filenamecount)
{
  int STATUS = 1;
  File root = fs.open(dirname);
  if (!root)
  {
    SERIAL_MST("Failed to open directory");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("Not a directory");
    return 0;
  }
  File file = root.openNextFile();
  while (file)
  {
    String namecount = readFile(LittleFS, filenamecount);
    fileCount = namecount.toInt();
    if (fileCount == 1)
    {
      STATUS = 0;
      break;
    }
    else
    {
      STATUS = checkFileSize(filenamecount);
      break;
    }
  }
  root.close();
  return STATUS;
}

int checkFileSize(String filenamecount)
{
  int filesize = {0};
  String namecount = readFile(LittleFS, filenamecount);
  fileCount = namecount.toInt();
  SERIAL_MST(String(fileCount));
  File file = LittleFS.open("/meterreading" + g_filename + String(fileCount));
  if (file)
  {
    filesize = file.size();
    file.close();
    SERIAL_MST("File size is : " + String(filesize));
    if (filesize > 25000)
    {
      return 1;
    }
    else
    {
      return 0;
    }
  }
  else
  {
    file.close();
    return 1;
  }
}

////////////////////////FUNCTIONS TO SUPPORT AT COMMANDS/////////////////////////

int lowRange(String Response)
{
  int range = 0;
  String buff = "";
  int temp = Response.indexOf(":") + 2;
  buff = Response.substring(temp, temp + 2);
  range = buff.toInt();
  // SERIAL_MST(String(range));
  return range;
}

void hardReset()
{
  pinMode(MODULE_RESET_4G, OUTPUT);
  digitalWrite(MODULE_RESET_4G, HIGH);
  delay(2500);
  digitalWrite(MODULE_RESET_4G, LOW);
//  appendFile(LittleFS, "/boardlogs", "Board restarted" + rtc.getTime("%A, %B %d %Y %H:%M:%S"));
  delay(10000);
  ESP.restart();
#if 0
  digitalWrite(MODULE_RESET_ESP,HIGH);
  delay(2500);
  digitalWrite(MODULE_RESET_ESP,LOW);
#endif
}

void CFUN()
{
  Serial2.print("AT+CFUN=0\r\n");
  SERIAL_MST("CFUN=0 Command given");
  delay(1000);
  Serial2.print("AT+CFUN=1\r\n");
  SERIAL_MST("CFUN=1 Command given");
  SERIAL_MST("Waiting 15 seconds");
  delay(15000);
  String response = "";
  while (Serial2.available())
  {
    if (Serial2.available())
    {
      char ch = Serial2.read();
      response += ch;
    }
  }
  SERIAL_MST(response);
}

String Serial4gATcommands(String command, String datatopost)
{
  String responsefrom4g = "";
  char command1[command.length()] = {0};
  int count = 0, length = command.length();
  command.toCharArray(command1, length + 1);

  //----------------------parsing-----------------------------------

  for (int i = 0; i < (command).length(); i++)
  {
    if (command[i] == '|')
    {
      count++;
    }
  }
  //    Serial.print(String(count));
  char *commands[count] = {0};
  char *token = strtok(command1, "|");
  int i = 0;
  while (token != NULL)
  {
    //      Serial.printf("%s\n", token);
    commands[i] = (token);
    token = strtok(NULL, "|");
    i++;
    if (i > count)
    {
      break;
    }
  }
  // SERIAL_MST(String(commands[0]));
  // SERIAL_MST(String(commands[1]));
  // SERIAL_MST(String(commands[2]));

  //------------------------------------------------------------
  clearserial2buffer();

  SERIAL_MST("REQ : " + String(commands[0]));
  Serial2.print(String(commands[0]) + "\r\n");
  int delay1 = atoi((commands[2]));
  delay(delay1);

  while (Serial2.available())
  {
    if (Serial2.available())
    {
      responsefrom4g = Serial2.readString();
    }
  }
  SERIAL_MST("RES : " + (responsefrom4g));
  if (responsefrom4g.indexOf(String(commands[1])) >= 0)
  {
    return responsefrom4g;
  }
  else if ((responsefrom4g.indexOf("ERROR") >= 0) || (responsefrom4g.indexOf("HTTPHEAD") >= 0))
  {
    return "error";
  }
  else if (responsefrom4g.indexOf("DOWNLOAD") >= 0)
  {
    SERIAL_MST("DATA \n" + (datatopost));
    Serial2.print(datatopost);
    delay(10000);
  }
  else if (responsefrom4g.length() <= 0)
  {

    SERIAL_MST("Resetting the module");
    int retryCount = 0;
    Serial2.print("AT+RESET\r\n");
    delay(15000);
    hardReset();
  }
  else
  {
  }
  return "0";
}


void writeNodeIDIntoFile(String commands)
{
  int k;
  String intr[6];
  int i = 0;
  for (int h = 0; h < 6; h++)
  {
    k = commands.indexOf("\n");
    commands = commands.substring(k + 1, commands.length());
    intr[i] = commands;
    // SERIAL_MST("String is :" + commands);
    i++;
  }
  String cmd_data_intr = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  SERIAL_MST("Command received = " + cmd_data_intr);
  cmd_data_intr.trim();
  if (cmd_data_intr != "0")
  {
    if ((cmd_data_intr.indexOf("NSTG") >= 0))
    {
      Serial.println(cmd_data_intr); 
      // Serial.print("Valid Node ID: ");
      writeFile("/NodeID/NodeID.txt", cmd_data_intr);
      
    }
  }
  else
  {
    SERIAL_MST("NO COMMANDS!");
  }
}
void parse_api_response(String url, String response)
{
  if (url.indexOf("/getgwserialinfo") >= 0)
  {
    setgwid(response);
  }
  else if (url.indexOf("gettime") >= 0)
  {
    timeResponseParser(response);
  }
  else if (url.indexOf("getcommands") >= 0)
  {
    writeCommandsIntoFile(response);
  }
  else if (url.indexOf("getsoftware") >= 0)
  {
    gw_urlParser(response);
  }
  else if (url.indexOf("getlatestnodeversion") >= 0)
  {
    node_urlParser(response);
  }
   else if(url.indexOf("getssidfrommac_v4g") >= 0)
  {
    writeNodeIDIntoFile(response);
  }
}

//------------------------------AT_POST------------------------------

int AT_POST(String payload, String httpdata, String url, int postcontentflag)
{
  int cfuncount = 0, poststatus = 0;
  String msgfrom4g = "";
  String authkey = readFile(LittleFS,"/authkey");
  String header_url = "AT+HTTPPARA=\"USERDATA\",secretkey:"+secretkey+"|OK|2000";
  String header_url1 = "AT+HTTPPARA=\"USERDATA\",authkey:"+authkey+"|OK|2000";
  Serial2.print("AT+HTTPTERM\r\n");
  delay(3000);
  digitalWrite(FOURG_COMMUNICATION, HIGH);  
  for (int i = 19; i < 27; i++)
  {
    if (i == 20)
    {
      msgfrom4g = Serial4gATcommands(url, "");
    }
    else if (i == 22)
    {
      msgfrom4g = Serial4gATcommands(header_url,"");
      msgfrom4g = Serial4gATcommands(header_url1,"");
      msgfrom4g = Serial4gATcommands(httpdata, payload);
    }
    else if ((postcontentflag == 1) && (i == 21))
    {
      msgfrom4g = Serial4gATcommands(AT_COMMAND[14], "");
    }
    else
    {
      msgfrom4g = Serial4gATcommands(AT_COMMAND[i], "");
    }

    //----------------------------------------------------------------------------------------------

    if (msgfrom4g.indexOf("error") >= 0)
    {
      CFUN();
      poststatus = 0;
      break;
    }
    else if (msgfrom4g.indexOf("200 OK") >= 0)
    {
      SERIAL_MST("200 RECEIVED");
      poststatus = 1;
    }
  }
  // SERIAL_MST(String(poststatus));
  digitalWrite(FOURG_COMMUNICATION, LOW);
  return poststatus;
}

//-----------------------------------------------AT_GET----------------------------------------

int AT_GET(String url)
{
  
  int cfuncount = 0, getsuccess = 0;
  String msgfrom4g = "";
  String authkey = readFile(LittleFS,"/authkey");
  String header_url = "AT+HTTPPARA=\"USERDATA\",secretkey:"+secretkey+"|OK|2000";
  String header_url1 = "AT+HTTPPARA=\"USERDATA\",authkey:"+authkey+"|OK|2000";
  Serial2.print("AT+HTTPTERM\r\n");
  delay(3000);
  digitalWrite(FOURG_COMMUNICATION, HIGH);
  for (int i = 12; i < 19; i++)
  {
//     SERIAL_MST(/(i));
    if(i == 15)
    {
      msgfrom4g = Serial4gATcommands(header_url, "");
      msgfrom4g = Serial4gATcommands(header_url1, "");
      msgfrom4g = Serial4gATcommands(AT_COMMAND[i], "");
    }
    else if (i != 13)
    {
      msgfrom4g = Serial4gATcommands(AT_COMMAND[i], "");
    }
    else
    {
       msgfrom4g = Serial4gATcommands(url, "");
    }

    if (msgfrom4g.indexOf("error") >= 0)
    {
      CFUN();
      getsuccess = 0;
      break;
    }
    else if (msgfrom4g.indexOf("AT+HTTPREAD") >= 0)
    {
      parse_api_response(url, msgfrom4g);
      getsuccess = 1;
    }
  }
  digitalWrite(FOURG_COMMUNICATION, LOW);
  return getsuccess;
}

int basicATcommands()
{
  for (int i = 0; i < 12; i++)
  {
    String msgfrom4g = Serial4gATcommands(AT_COMMAND[i], "");
    if (msgfrom4g.indexOf("AT+CSQ") >= 0)
    {
       global_range = lowRange(msgfrom4g);
      if (global_range < 9)
      {
        String msgfrom4g = Serial4gATcommands("AT+RESET|OK|15000", "");
        SERIAL_MST("Low range Detected");
        SERIAL_MST(String(global_range));
        hardReset();
      }
    }
    else if (msgfrom4g.indexOf("AT+CICCID") >= 0)
    {
      int index = msgfrom4g.indexOf(':');
      ciccid = msgfrom4g.substring(index + 2);
      index = ciccid.indexOf('\n');
      ciccid = ciccid.substring(0, index);
      ciccid.trim();
    }
    else if (msgfrom4g.indexOf("AT+SIMEI") >= 0)
    {
      int index = msgfrom4g.indexOf(':');
      simeino = msgfrom4g.substring(index + 2);
      index = simeino.indexOf('\n');
      simeino = simeino.substring(0, index);
      simeino.trim();
      writeFile("/IMEI",simeino);
    }
    else if ((msgfrom4g.indexOf("NO SERVICE") >= 0))
    {
      String msgfrom4g = Serial4gATcommands("AT+RESET|OK|15000", "");
      i = 0;
    }
    else
    {
    }
  }
  return 1;
}

void setgwid(String res)
{
  int k;
  String intr[6];
  int i = 0;
  for (int h = 0; h < 6; h++)
  {
    k = res.indexOf("\n");
    res = res.substring(k + 1, res.length());
    intr[i] = res;
    i++;
  }
  String cmd_data_intr = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  SERIAL_MST("Command received = " + cmd_data_intr);
  cmd_data_intr.trim();
  if ((cmd_data_intr.indexOf("NSGW") >= 0) && cmd_data_intr.length() == 10)
  {
    writeFile("/NodeID/NodeID.txt", cmd_data_intr);
    SERIAL_MST("Node ID Configured Successfully");
    GWID = readFile(LittleFS, "/NodeID/NodeID.txt");
    SERIAL_MST(GWID);
  }
  else
  {
    SERIAL_MST("Filewriting failed");
  }
}

void timeResponseParser(String response)
{
  // Code to parse the time
  int ref = response.indexOf("/");
  int Hour1 = response[ref - 2] - '0', Hour0 = response[ref - 1] - '0', Minute1 = response[ref + 1] - '0', Minute0 = response[ref + 2] - '0', Hour2 = response[ref + 4] - '0', Hour3 = response[ref + 5] - '0', Hour4 = response[ref + 7] - '0', Hour5 = response[ref + 8] - '0', Hour6 = response[ref + 10] - '0', Hour7 = response[ref + 11] - '0', Hour8 = response[ref + 13] - '0', Hour9 = response[ref + 14] - '0';
  int Month = ((Hour1 * 10) + (Hour0)), Day = ((Minute1 * 10) + (Minute0)), Year = ((Hour2 * 10) + (Hour3)), Hour = ((Hour4 * 10) + (Hour5)), Minute = ((Hour6 * 10) + (Hour7)), Second = ((Hour8 * 10) + (Hour9));
  String date = String(Day) + String(Month) + String(Year);
  delay(500);
  rtc.setTime(Second, Minute, Hour, Day, Month, 2000 + Year); // 14th Apr 2022 10:42:30
  SERIAL_MST("Gateway time set as : " + String(rtc.getTime("%A, %B %d %Y %H:%M:%S")));
  
  // Code to parse the gateway and node latest version
  char *token;
  char tempbuff[100] = {};
  String tempstr[3] = {""};
  int i = 0, download_first_time = 0;
  response.toCharArray(tempbuff, response.length() + 1);
  const char *delimiter = ",";
  for (token = strtok(tempbuff, delimiter); token != NULL; i++)
  {
    tempstr[i] = String(token);
    token = strtok(NULL, delimiter);
  }
  float gw_new_firmware_version = tempstr[1].toFloat();
  // float node_new_firmware_version = tempstr[2].substring(2).toFloat();
  // node_new_firmware_version = 7.2;
  String authorizationkey = tempstr[2];
  authorizationkey.trim();
  String authdata = readFile(LittleFS,"/authkey");
  authdata.trim();
  if(authorizationkey.length()>0 && authorizationkey != authdata)
  {
    writeFile("/authkey",String(authorizationkey));
  }
  SERIAL_MST("GWFW = " + String(gw_new_firmware_version));
  // SERIAL_MST("NodeFW = " + String(node_new_firmware_version));
  writeFile("/gatewaylatestversion", String(gw_new_firmware_version));
  // writeFile("/nodelatestversion", String(node_new_firmware_version));
}

void OTAUpdater()
{
  // Code to update gateway
  float gw_new_firmware_version = readFile(LittleFS, "/gatewaylatestversion").toFloat();
  if (gw_new_firmware_version > gw_current_firmware_version)
  {
    SERIAL_MST("New Gateway firmware found!\n");
    SERIAL_MST("Deleting node OTA file now");
    deleteFile(LittleFS, "/nodeotadownload.bin");
    String otastatus = readFile(LittleFS, "/gwotastatus");
    if (otastatus != "1111")
    {
      SERIAL_MST("Getting GW OTA urls now");
      // enable the below url to reroute the request to 172 server
      //  String url = "AT+HTTPPARA=\"URL\",\"http://configurations.ms-tech.in:9838/getlatestgwversion_test?gwid=" + GWID + "&cv=" + String(gw_current_firmware_version) + "\"" + "|OK|2000";

      String url = "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/getsoftware?gwid=" + GWID + "&rv=" + String(gw_new_firmware_version) + "\"" + "|OK|2000";
      SERIAL_MST(url);
      int success = 0;
      for (int i = 0; i < 2; i++)
      {
        success = AT_GET(url);
        if (success == 1)
        {
          SERIAL_MST("------------------get success----------------");
          break;
        }
      }
      if (success == 1)
      {
        SERIAL_MST("Get url successfull!");
        if (String(gw_otaurl[0]).indexOf("1.0") >= 0)
        {
          SERIAL_MST("NO OTA AVAILABLE FOR GATEWAY!");
        }
        else
        {
          int downloadfilestatus = 0;
          downloadfilestatus = downloadFile_read4GFileSystem(1);
          if (downloadfilestatus == 1)
          {
            SERIAL_MST("GATEWAY OTA FILE DOWNLOAD SUCCESSFULL!");
          }
          else
          {
            SERIAL_MST("GATEWAY OTA FILE DOWNLOAD FAILED!");
          }
        }
      }
    }

    otastatus = readFile(LittleFS, "/gwotastatus");
    if (otastatus == "1111")
    {
      String msgfrom4g = Serial4gATcommands("AT+RESET|OK|15000", "");
      hardReset();
    }
  }
}

//------------------------------------------gettime----------------------------------------------------------------------

int syncTimeWithServer()
{
  int timestatus = 0, success = 0 , availentryforbill = 0;
  String url = String(AT_COMMAND[13]);
  GWID.trim();
  String macid = "&mac=" + WiFi.macAddress();
  String amemory = String(LittleFS.totalBytes() - LittleFS.usedBytes());
  SERIAL_MST("TOTAL AVAILABLE MEMORY " +String(LittleFS.totalBytes() - LittleFS.usedBytes()));
  availentryforbill = ReadMSNFromFile("/availableentry").toInt();
  if (GWID.indexOf("NSGW") == 0)
  {
    (url) = (url) + GWID + "&cfc=" + cfc + macid + "&csq=" + global_range + "&cv=" + String(gw_current_firmware_version) + "&cid=" + ciccid + "&imei=" + simeino + "&availmemory=" + amemory + "&billentries=" + availentryforbill +"&meterslno=" + MeterSerialNo_Final + "\"" + "|OK|2000";
  }
  else
  {
    String macid = WiFi.macAddress();
    macid.replace(":", "");
    (url) = (url) + macid + "&cfc=" + cfc + FourGresponse + "&csq=" + global_range + "&cv=" + String(gw_current_firmware_version) + "&ciccid=" + ciccid + "&simei=" + simeino + "&availmemory=" + amemory + "&billentries=" + availentryforbill + "&meterslno=" + MeterSerialNo_Final + "\"" + "|OK|2000";
  }

  for (int i = 0; i < 2; i++)
  {
    success = AT_GET(url);
    if (success == 1)
    {
      SERIAL_MST("------------------get success----------------");
      break;
    }
  }

  return success;
}

//------------------------------------------getcommands----------------------------------------------------------------------

int getcommands_old()
{
  int commandstatus = 0, success = 0;
  String url = "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/getcommands?gwid=";
  GWID.trim();
  if (GWID.indexOf("NSGW") == 0)
  {
    url = url + GWID + "\"" + "|OK|2000";
  }
  else
  {
    String macid = WiFi.macAddress();
    macid.replace(":", "");
    url = url + macid + "\"" + "|OK|2000";
  }

  for (int i = 0; i < 2; i++)
  {
    success = AT_GET(url);
    if (success == 1)
    {
      SERIAL_MST("------------------get success----------------");
      break;
    }
  }
  return success;
}


int postNodeFileNames()
{
  int postsuccess = 0;
  String at_httpdata = "";
  String APItosendnodefilenames = "";
  String payload = readFile(LittleFS, "/filenameslist");
  payload = "{\"data2\":\"" + payload + "\",\"gwid\":\"" + GWID + "\"}";
  int fsize = payload.length(); // GET THE FILE SIZE TO POST
  SERIAL_MST("File size Posted : " + String(fsize));
  at_httpdata = "AT+HTTPDATA=" + String(fsize) + ",1000|OK|3000"; // PREPARE THE COMMAND
  APItosendnodefilenames = String(AT_COMMAND[29]);
  for (int i = 0; i < 2; i++)
  {
    postsuccess = AT_POST(payload, at_httpdata, APItosendnodefilenames, 2);
    if (postsuccess == 1)
    {
      SERIAL_MST("------------------POST success----------------");
      break;
    }
  }
  return postsuccess;
}

//--------------------------------------------POST NODELIST-----------------------------------------------

int postNodeList()
{
  int postsuccess = 0;
  String at_httpdata = "";
  String APItosendnodelist = "";
  String payload = readFile(LittleFS, "/scanDevices");
  if (payload != "error")
  {
    payload = "data2=" + payload; // APPEND THE CONTAINER TO POST TO SERVER
    SERIAL_MST(payload);
    int fsize = payload.length(); // GET THE FILE SIZE TO POST
    SERIAL_MST(String(fsize));
    // postSuccess = 0;
    if (fsize > 6)
    {
      at_httpdata = "AT+HTTPDATA=" + String(fsize) + ",1000|OK|3000"; // PREPARE THE COMMAND
      APItosendnodelist = String(AT_COMMAND[27]);
      for (int i = 0; i < 2; i++)
      {
        postsuccess = AT_POST(payload, at_httpdata, APItosendnodelist, 2);
        if (postsuccess == 1)
        {
          SERIAL_MST("------------------POST success----------------");
          break;
        }

      } //      SERIAL_MST(String(postsuccess));
      if (postsuccess == 1)
      {
        SERIAL_MST("NODE list posted successfully");

        deleteFile(LittleFS, "/scanDevices");
        SERIAL_MST("Node list file posted successfully. Size : " + String(fsize));
        SERIAL_MST("-------------------------POST NODELIST SUCCESS-------------------------");
      }
      else
      {
        SERIAL_MST("-------------------------POST NODELIST FAILURE-------------------------");
      }
    }
  }
  else
  {
    SERIAL_MST("No nodes found");
  }
  return postsuccess;
}

//--------------------------------------------POST DATA-----------------------------

int postNodeData()
{
  int poststatus = 0;
  String at_httpdata = "", APItosendnodedata = "", localfilename = "";
  int fsize = 0, postsuccess = 0;
  File root = LittleFS.open("/meterreading");
  if (!root)
  {
    SERIAL_MST("Directory not found!");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("It is not a Directory");
    return 0;
  }
  File file = root.openNextFile();
  if (file)
  {
    while (file)
    {
      localfilename = file.name();
      delay(1000);
      SERIAL_MST("File name : " + localfilename);
      SERIAL_MST("GW name : " + GWID);
      String payload = readFile(LittleFS, "/meterreading/" + String(localfilename));
      GWID.trim();
      if (payload.length() == 0)
      {
        payload = "0";
      }
      if (payload != "0")
      {
        String temp_gwid = "";
        GWID.trim();
        if (GWID.indexOf("NSGW") != 0)
        {
          String macid = WiFi.macAddress();
          macid.replace(":", "");
          temp_gwid = macid;
        }
        else
        {
          temp_gwid = GWID;
        }
        payload = "{\"data2\":\"" + payload + "\",\"gwid\":\"" + temp_gwid + "\"}"; // APPEND THE CONTAINER TO POST TO SERVER
        fsize = payload.length();                         // GET THE FILE SIZE TO POST
        at_httpdata = "AT+HTTPDATA=" + String(fsize) + ",1000|OK|3000";       // PREPARE THE COMMAND
        APItosendnodedata = String(AT_COMMAND[20]);

        for (int i = 0; i < 2; i++)
        {
          postsuccess = AT_POST(payload, at_httpdata, APItosendnodedata, 2);
          if (postsuccess == 1)
          {
            SERIAL_MST("------------------POST success----------------");
            break;
          }
        }
        if (postsuccess == 1)
        {
          file.close();

          deleteFile(LittleFS, "/meterreading/" + String(localfilename));

          SERIAL_MST("Data file posted successfully. Size : " + String(fsize));
          SERIAL_MST("-------------------------POST NODEDATA SUCCESS-------------------------");
        }
        else
        {
          SERIAL_MST("-------------------------POST NODEDATA FAILURE-------------------------");
        }
      }

      else
      {
        SERIAL_MST("Data is empty in file ");
      }
      file = root.openNextFile();
    }
  }
  else
  {
    SERIAL_MST("No files present in directory to post");
  }
  file.close();
  root.close();
  return postsuccess;
}

int postNodeTestingData()
{
  int poststatus = 0;
  String at_httpdata = "", APItosendnodedata = "", localfilename = "";
  int fsize = 0, postsuccess = 0;
  File root = LittleFS.open("/testreading");
  if (!root)
  {
    SERIAL_MST("Directory not found!");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("It is not a Directory");
    return 0;
  }
  File file = root.openNextFile();
  if (file)
  {
    while (file)
    {
      localfilename = file.name();
      delay(1000);
      SERIAL_MST("File name : " + localfilename);
      SERIAL_MST("GW name : " + GWID);
      String payload = readFile(LittleFS, "/testreading/" + String(localfilename));
      GWID.trim();
      if (payload.length() == 0)
      {
        payload = "0";
      }
      if (payload.length() > 0)
      {
        String temp_gwid = "";
        GWID.trim();
        if (GWID.indexOf("NSGW") != 0)
        {
          String macid = WiFi.macAddress();
          macid.replace(":", "");
          temp_gwid = macid;
        }
        else
        {
          temp_gwid = GWID;
        }
        payload = "{\"data2\":\"" + payload + "\",\"gwid\":\"" + temp_gwid + "\"}"; // APPEND THE CONTAINER TO POST TO SERVER
        fsize = payload.length();                         // GET THE FILE SIZE TO POST
        at_httpdata = "AT+HTTPDATA=" + String(fsize) + ",1000|OK|3000";       // PREPARE THE COMMAND
        APItosendnodedata = String(AT_COMMAND[33]);
        SERIAL_MST(payload);
        for (int i = 0; i < 2; i++)
        {
          postsuccess = AT_POST(payload, at_httpdata, APItosendnodedata, 2);
          if (postsuccess == 1)
          {
            SERIAL_MST("------------------POST success----------------");
            break;
          }
        }
        if (postsuccess == 1)
        {
          file.close();

          deleteFile(LittleFS, "/testreading/" + String(localfilename));

          SERIAL_MST("Data file posted successfully. Size : " + String(fsize));
          SERIAL_MST("-------------------------POST NODEDATA SUCCESS-------------------------");
        }
        else
        {
          SERIAL_MST("-------------------------POST NODEDATA FAILURE-------------------------");
        }
      }

      else
      {
        SERIAL_MST("Data is empty in file ");
      }
      file = root.openNextFile();
    }
  }
  else
  {
    SERIAL_MST("No files present in directory to post");
  }
  file.close();
  root.close();
  return postsuccess;
}

int postIPLData()
{
  int poststatus = 0;
  String at_httpdata = "", APItosendnodedata = "", localfilename = "";
  int fsize = 0, postsuccess = 0;
  File root = LittleFS.open("/IPLreading");
  if (!root)
  {
    SERIAL_MST("Directory not found!");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("It is not a Directory");
    return 0;
  }
  File file = root.openNextFile();
  if (file)
  {
    while (file)
    {
      localfilename = file.name();
      delay(1000);
      SERIAL_MST("File name : " + localfilename);
      SERIAL_MST("GW name : " + GWID);
      String payload = readFile(LittleFS, "/IPLreading/" + String(localfilename));
      GWID.trim();
      if (payload.length() == 0)
      {
        payload = "0";
      }
      
      if (payload.length()> 0)
      {
        String temp_gwid = "";
        GWID.trim();
        if (GWID.indexOf("NSGW") != 0)
        {
          String macid = WiFi.macAddress();
          macid.replace(":", "");
          temp_gwid = macid;
        }
        else
        {
          temp_gwid = GWID;
        }
        payload = "{\"data2\":\"" + payload + "\",\"gwid\":\"" + temp_gwid + "\"}"; // APPEND THE CONTAINER TO POST TO SERVER
        fsize = payload.length();                         // GET THE FILE SIZE TO POST
        at_httpdata = "AT+HTTPDATA=" + String(fsize) + ",1000|OK|3000";       // PREPARE THE COMMAND
        APItosendnodedata = String(AT_COMMAND[20]);

        for (int i = 0; i < 2; i++)
        {
          postsuccess = AT_POST(payload, at_httpdata, APItosendnodedata, 2);
          if (postsuccess == 1)
          {
            SERIAL_MST("------------------POST success----------------");
            break;
          }
        }
        if (postsuccess == 1)
        {
          file.close();

          deleteFile(LittleFS, "/IPLreading/" + String(localfilename));

          SERIAL_MST("Data file posted successfully. Size : " + String(fsize));
          SERIAL_MST("-------------------------POST NODEDATA SUCCESS-------------------------");
        }
        else
        {
          SERIAL_MST("-------------------------POST NODEDATA FAILURE-------------------------");
        }
      }

      else
      {
        SERIAL_MST("Data is empty in file ");
      }
      file = root.openNextFile();
    }
  }
  else
  {
    SERIAL_MST("No files present in directory to post");
  }
  file.close();
  root.close();
  return postsuccess;
}

//--------------------------------postbilling--------------------------------

String Serial4gBill(String command,String post_fname="",int fsize = 0)
{
  SERIAL_MST("Length passed = "+String(fsize));
  String responsefrom4g = "";
  char command1[command.length()] = {0};
  int count = 0, length = command.length();
  command.toCharArray(command1, length + 1);

  //----------------------parsing-----------------------------------

  for (int i = 0; i < (command).length(); i++)
  {
    if (command[i] == '|')
    {
      count++;
    }
  }
  //    Serial.print(String(count));
  char *commands[count] = {0};
  char *token = strtok(command1, "|");
  int i = 0;
  while (token != NULL)
  {
    //      Serial.printf("%s\n", token);
    commands[i] = (token);
    token = strtok(NULL, "|");
    i++;
    if (i > count)
    {
      break;
    }
  }
  // SERIAL_MST(String(commands[0]));
  // SERIAL_MST(String(commands[1]));
  // SERIAL_MST(String(commands[2]));

  //------------------------------------------------------------
  clearserial2buffer();

  SERIAL_MST("REQ : " + String(commands[0]));
  Serial2.print(String(commands[0]) + "\r\n");
  int delay1 = atoi((commands[2]));
  delay(delay1);

  while (Serial2.available())
  {
    if (Serial2.available())
    {
      responsefrom4g = Serial2.readString();
    }
  }
  SERIAL_MST("RES : " + (responsefrom4g));
  if (responsefrom4g.indexOf(String(commands[1])) >= 0)
  {
    if (responsefrom4g.indexOf("CFTRANRX") >= 0)
    {
      
      SERIAL_MST("DATA TRANSFER STARTED!");
      SERIAL_MST(String(fsize));
      int readbyte = 10000;
      int num_loops = (fsize / readbyte);
      SERIAL_MST(String(num_loops));
      File file = LittleFS.open(post_fname,"r");
      for (int i = 0; i <= num_loops; i++)
      { 
        String finaldata = "";
        
         if(i == num_loops)
         {
           readbyte = fsize - num_loops*readbyte; 
         }
        for(int i=0;i<readbyte;i++)
        {
            char ch = file.read();
            finaldata = finaldata + String(ch);
            
        }
          SERIAL_MST("the data is length "+String(finaldata));
          int count = 10000*(i+1);
          file.seek(count, SeekSet);
          if(finaldata.length()>0)
          {
            Serial2.print(finaldata);
            delay(1000);
          }
          
      }
     
      SERIAL_MST("DATA TRANSFER COMPLETE!");
      delay(10000);
    
    }
    else
    {
      return responsefrom4g;
    }
  }
  else if ((responsefrom4g.indexOf("ERROR") >= 0) || (responsefrom4g.indexOf("HTTPHEAD") >= 0))
  {
    return "error";
  }
  
  else if (responsefrom4g.length() <= 0)
  {

    SERIAL_MST("Resetting the module");//hardreset
    int retryCount = 0;
    Serial2.print("AT+RESET\r\n");
    delay(15000);
    hardReset();
  }
  else
  {
  }
  return "0";
}


int writeFile_into_4g(String path_local, String path_4g)
{
    int cfuncount = 0, poststatus = 1;
    String msgfrom4g = "";
    String payload3 = readFile(LittleFS, (path_local));
    String cftranrx_cmd = String(AT_COMMANDS_FILETRANSFER[3]) + "\"" + path_4g + "\"," + String(payload3.length()) + "|>|2000";
    for (int i = 0; i < 5; i++)
    {
      if (i == 3)
      {
        msgfrom4g = Serial4gBill(cftranrx_cmd, path_local,payload3.length());
      }
      else
      {
        msgfrom4g = Serial4gBill(AT_COMMANDS_FILETRANSFER[i], "");
      }

      //----------------------------------------------------------------------------------------------

      if (msgfrom4g.indexOf("error") >= 0)
      {
        CFUN();
        poststatus = 0;
        break;
      }
      else
      {
        poststatus = 1;
      }
    }
  // SERIAL_MST("Status = " + String(poststatus));
  return poststatus;
}

int AT_POST_FILE(String path_4g, String url)
{
  
  delay(10000);
  url = String(AT_COMMANDS_POSTFILE[1]) + ",\"" + url + "\"|OK|2000";
  String httppostfile = String(AT_COMMANDS_POSTFILE[3]) + path_4g + "\",1,1,1|OK|10000";
  String authkey = readFile(LittleFS,"/authkey");
  String header_url = "AT+HTTPPARA=\"USERDATA\",secretkey:"+secretkey+"|OK|2000";
  String header_url1 = "AT+HTTPPARA=\"USERDATA\",authkey:"+authkey+"|OK|2000";
 
  int cfuncount = 0, poststatus = 0;
  String msgfrom4g = "";

  // Serial2.print("AT+HTTPTERM\r\n");
  // delay(3000);

  for (int i = 0; i < 7; i++)
  {
    if (i == 1)
    {
      msgfrom4g = Serial4gBill(url, "");
    }
    else if (i == 3)
    {
      msgfrom4g = Serial4gBill(header_url, "");
      msgfrom4g = Serial4gBill(header_url1, "");
      msgfrom4g = Serial4gBill(httppostfile, "");
    }
    else
    {
      msgfrom4g = Serial4gBill(AT_COMMANDS_POSTFILE[i], "");
    }

    //----------------------------------------------------------------------------------------------

    if (msgfrom4g.indexOf("error") >= 0)
    {
      CFUN();
      poststatus = 0;
      break;
    }
    else if (msgfrom4g.indexOf("200 OK") >= 0)
    {
      SERIAL_MST("200 RECEIVED");
      // Make the flag 1 indicating to delete the file in 4G module as posting is successfull
      poststatus = 1;
    }
  }
  // SERIAL_MST(String(poststatus));
  return poststatus;
}

int postBillData()
{
         String APItoPostBillData = "", localfilename = "";
          int fsize = 0, postsuccess = 0;
          File root = LittleFS.open("/BData");
          if (!root)
          {
            SERIAL_MST("Directory not found!");
            return 0;
          }
          if (!root.isDirectory())
          {
            SERIAL_MST("It is not a Directory");
            return 0;
          }
          File file = root.openNextFile();
          if (file)
          {
            while (file)
            {
              localfilename = "/BData/" + String(file.name());
              delay(1000);
              SERIAL_MST("File name : " + localfilename);
              SERIAL_MST("GW name : " + GWID);
              file.close();
              String filename_4G = "c:/billData.txt";
              String filename_4G_trimmed = filename_4G.substring(filename_4G.indexOf("/"));
              filename_4G.trim();
//              APItoPostBillData = "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:16002/senddata_v2\"|OK|2000";
              APItoPostBillData = String(AT_COMMAND[20]);
             for (int i = 0; i < 2; i++)
               {
                  int fileWriteStatus = writeFile_into_4g(localfilename,filename_4G);
        
                  if (fileWriteStatus == 1)
                  {
                      SERIAL_MST("File Writing successfull");
                    
                      postsuccess = AT_POST_FILE(filename_4G_trimmed, APItoPostBillData);
                      if (postsuccess == 1)
                      {
                        SERIAL_MST("------------------POST success----------------");
                        break;
                      }
                  }
                  else
                  {
                    SERIAL_MST("File Writing unsuccessfull");
                  }
               }
                if(postsuccess == 1)
                {
                  file.close();
        
                  deleteFile(LittleFS, String(localfilename));
        
                  // Delete the file in 4G module as posting is successfull
                  String deleteCommand = "AT+FSDEL=" + filename_4G_trimmed + "|OK|2000";
                  Serial4gBill(deleteCommand, "");
                  String memCommand = "AT+FSMEM|OK|2000";
                  Serial4gBill(memCommand, "");
        
                  SERIAL_MST("Data file posted successfully. Size : " + String(fsize));
                  SERIAL_MST("-------------------------POST BILL DATA SUCCESS-------------------------");
                }
                else
                {
                  SERIAL_MST("-------------------------POST BILL DATA FAILURE-------------------------");
                }
              file = root.openNextFile();
            }
           
          }
          else
          {
            SERIAL_MST("No files present in directory to post");
          }
          file.close();
          root.close();
          return postsuccess;
}




//------------------------------------------------------------------------------------------------

 
int memoryCheck()
{
  int success = 0;
  SERIAL_MST("Bytes used :" + String(LittleFS.usedBytes()));
  if (LittleFS.usedBytes() > 1000000)
  {
    SERIAL_MST("GATEWAY IS FULL");
    String url = String(AT_COMMAND[28]);

    GWID.trim();
    if (GWID.indexOf("NSGW") == 0)
    {
      url = url + GWID + "\"" + "|OK|2000";
    }
    else
    {
      String macid = WiFi.macAddress();
      macid.replace(":", "");
      url = url + macid + "\"" + "|OK|2000";
    }

    for (int i = 0; i < 2; i++)
    {
      success = AT_GET(url);
      if (success == 1)
      {
        SERIAL_MST("------------------get success----------------");
        break;
      }
    }

    if (success == 1)
    {

      SERIAL_MST("-------------------------GETCOMMANDS SUCCESS-------------------------");
      return success;
    }
    else
    {
      SERIAL_MST("-------------------------GETCOMMANDS FAILURE-------------------------");
    }
  }
  else
  {

    return 0;
  }
}

int LocalNetworkReader()
{
  int stat = 0;
  delay(100);
  int statusforgatewayfull = memoryCheck();
  if (statusforgatewayfull == 0)
  {
    stat = GetFileListfromNode();
    stat = GetIPLfromNode();
  }

  else
  {
    stat = 0;
  }
  return stat;
}


void clearserial2buffer()
{
  unsigned long lastMillis;  
  lastMillis = millis();
  const unsigned long period = 1000;

  while (Serial2.available())
  {
    if (millis() - lastMillis >= period)
    {
      break;
    }
    else
    {
        Serial2.read();
        Serial.read();
    }
  }
}

int internetDataSender()
{
//  SERIAL_MST("Status of internetDataSend/er = " + String(status));
  int status = 0, timestatus = 0, commandstatus = 0, datastatus = 0, nodeliststatus = 0, nodefilenamestatus = 0;
  int is_4g_ready = 0;
  clearserial2buffer();
 is_4g_ready = basicATcommands();

 if (is_4g_ready)
 {
    timestatus = syncTimeWithServer();
    OTAUpdater();

    datastatus = postNodeData();
    postIPLData();
    postBillData();

    // nodeliststatus = postNodeList();
// Removed in V6.2 on 25nov
#if 0
        nodefilenamestatus = postNodeFileNames();
#endif
 }
 else
 {
   SERIAL_MST("Module not ready");
 }
  if (timestatus == 1 && commandstatus == 1 && datastatus == 1 && nodeliststatus == 1 && nodefilenamestatus == 1)
  {
    status = 1;
  }
  else
  {
    status = 0;
  }
  SERIAL_MST("Status of internetDataSender = " + String(status));
  return status;
}

void SERIAL_MST(String payload)
{
  if (debug_flag == 1)
  {
    delay(10);
    Serial.println(payload);
  }
  seriallogger_string(payload);
}

void delete_commands(String dirname)
{
  File root = LittleFS.open(dirname);
  if (!root)
  {
    SERIAL_MST("Failed to open directory");
    return;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("Not a directory");
    return;
  }

  File file = root.openNextFile();
  while (file)
  {
    String filename_l = file.name();
    SERIAL_MST(filename_l);
    file.close();
    deleteFile(LittleFS, "/commands/" + filename_l);
    file = root.openNextFile();
  }
  SERIAL_MST("All command files are deleted");
  root.close();
  return;
}

String node_serialization(int build_id)
{
  File file = LittleFS.open("/NodeID/NodeID.txt", "r");
  String macaddr = WiFi.macAddress();
  Serial.print("mac : " + macaddr);
  String mainURL = "http://172.104.244.42:9838/getssidfrommac_v4g?buildid=" + String(build_id) + "&mac=" + macaddr;
  String payload;
  int retryCount = 0;
  String nodedata = "0";

  if (!file)
  {
    createDir(LittleFS, "/NodeID");

    Serial.println("\r\nConfigure Node ID: ");
    WiFi.begin("Airtel_9986025401", "air72052");

//     WiFi.be/gin("PavanPhone", "Pavan@97");
    while (WiFi.status() != WL_CONNECTED)
    {
      Serial.println("--");
      delay(1000);
      if (retryCount == 10)
      {
        nodedata = "0";
        break;
      }
      retryCount++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
      WiFiClient client;
      HTTPClient http;
//       Serial.print("[HTTP] begin...\n");
       
      if (http.begin(client, mainURL))
      { // HTTP
//         Serial.print("[HTTP] GET...\n");
       

        // start connection and send HTTP header
        int httpCode = http.GET();

        // httpCode will be negative on error
        if (httpCode > 0)
        {
          // HTTP header has been send and Server response header has been handled
//           Serial.printf("[HTTP] GET... code: %d\n", httpCode);
       
          // file found at server
          if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY)
          {
            payload = http.getString();
             Serial.println(payload);
            http.end();
          }
        }
        else
        {
          // Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
          http.end();
        }
        // http.end();
      }
      else
      {
        // Serial.printf("[HTTP} Unable to connect\n");
      }

      
    }
    // Serial.println("length is " + String(payload.length()));
    if ((payload.indexOf("NSTG") >= 0))
    {
      Serial.println(payload);
      // Serial.print("Valid Node ID: ");
      writeFile("/NodeID/NodeID.txt", payload);

      // WritePostDataIntoBlockIDFile("/NodeID/NodeID.txt", payload);
      // Serial.println("Node ID Configured Successfully");
      nodedata = readFile(LittleFS, "/NodeID/NodeID.txt");
      // nodedata = ReadMSNFromFile("/NodeID/NodeID.txt");
      // Serial.print(nodedata);

      // digitalWrite(RELAY_OFF, HIGH);
      // delay( 1000 );
      // digitalWrite(RELAY_OFF, LOW);
      // delay( 2000 );

      // digitalWrite(RELAY_ON, HIGH);
      // delay( 1000 );
      // digitalWrite(RELAY_ON, LOW);
      // delay( 1000 );
      // WritePostDataIntoBlockIDFile("/RelayStatus/status.txt", "1");
    }
    else
    {
      // Serial.println("filewriting failed");
    }
  }
  else
  {
    file.close();
    // read node id from file and assign it to a variable
    nodedata = ReadMSNFromFile("/NodeID/NodeID.txt");

    //    Serial.println("Global node id is " + global_NodeID);
  }

    
    
  return nodedata;
}

// /// OTA software code.
// void progressCallBack(size_t currSize, size_t totalSize)
// {
//  SERIAL_MST("CALLBACK:  Update process at "+String(currSize)+" of "+String(totalSize)+" bytes...\n");
// }

// void handleupdatefirmware()
// {
//  SERIAL_MST("\nSearch for firmware..");
//  File firmware = LittleFS.open("/gwotadownload.bin", "r");
//  SERIAL_MST(String(firmware.size()));
//  if (firmware)
//  {
//    SERIAL_MST(F("found!"));
//    SERIAL_MST(F("Try to update!"));
//    Update.onProgress(progressCallBack);
//    Update.begin(firmware.size(), U_FLASH);
//    Update.writeStream(firmware);
//    if (Update.end())
//    {
//      SERIAL_MST(F("Update finished!"));
//      // SERIAL_MST(millis());
//      ESP.restart();
//    }
//    else
//    {
//      SERIAL_MST(F("Update error!"));
//      SERIAL_MST(String(Update.getError()));
//    }
//    // Updateflag = 1;
//    firmware.close();
//  }
//  else
//  {
//    SERIAL_MST(F("Not found!"));
//  }
// }

//////////////////////////////////////////////////////////
int downloadFile_read4GFileSystem(int flag)
{
  // here flag variable defines which firmware is being downloaded.
  // Value of 1 should be passsed to this function if gateway firmware is to be downloaded
  // Value of 2 should be passsed to this function if node firmware is to be downloaded
  int gwstatus = 0, nodestatus = 0, status = 0;
  if (flag == 1)
  {
    SERIAL_MST("Downloading GW OTA file now");
    for (int i = 0; i < 2; i++)
    {
      SERIAL_MST("URL" + String(i + 1) + " = " + gw_otaurl[i]);
    }
  }
  else if (flag == 2)
  {
    SERIAL_MST("Downloading NODE OTA file now");
    SERIAL_MST("URL = " + nodeotaurl);
  }
  int fileTransferStatus = 0;
  // int retrycount = 0;
  if (flag == 1)
  {
    File download_file = LittleFS.open("/gwotadownload.bin", "w");
    for (int chunk_num = 0; chunk_num < 2; chunk_num++)
    {
      fileTransferStatus = 0;
      gw_otaurl[chunk_num].trim();

      String otaUrl = String(OTA_COMMANDS[2])+String(gw_otaurl[chunk_num])+"\"|OK|2000";
      String httpReadCommand = String(OTA_COMMANDS[6]) + "gwotaupdate" + String(chunk_num) + ".bin" + "\"|OK|3000";

      int filedownloadStatus = 0;
      filedownloadStatus = AT_POST_OTA(otaUrl, httpReadCommand);
      // AT_downloadFile(gw_otaurl[chunk_num], "gwotaupdate" + String(chunk_num) + ".bin");

      if(filedownloadStatus == 1)
      {
        if(chunk_num == 0)
        {
          // retrycount = 0;
          writeFile("/gwotastatus", "1000");
          fileTransferStatus = read4GFileSystem("gwotaupdate" + String(chunk_num) + ".bin", download_file);

          if (fileTransferStatus == 1)
          {
            SERIAL_MST("read4GFileSystem success in chunk 1");
            writeFile("/gwotastatus", "1100");
          }
          else
          {
            SERIAL_MST("read4GFileSystem failed during chunk 1");
            break;
          }
        }
        else if(chunk_num == 1)
        {
          // retrycount = 0;
          writeFile("/gwotastatus", "1110");
          // readFile(LittleFS,"/gwotastatus");
          fileTransferStatus = read4GFileSystem("gwotaupdate" + String(chunk_num) + ".bin", download_file);
          if (fileTransferStatus == 1)
          {
            SERIAL_MST("read4GFileSystem success in chunk 2");
            writeFile("/gwotastatus", "1111");
            // readFile(LittleFS,"/gwotastatus");
            gwstatus = 1;
            break;
          }
          else
          {
            SERIAL_MST("read4GFileSystem failed during chunk 2");
            break;
          }
        }
      }
      else{
        SERIAL_MST("Download Failed!");
      }

      // else
      // {
      //  // retry for previous chunk as downloading has failed
      //  chunk_num--;
      //  retrycount++;
      //  gwstatus = 0;
      //  if (retrycount == 2)
      //  {
      //    download_file.close();
      //    break;
      //  }
      //  else
      //  {
      //    CFUN();
      //  }
      // }
    }
    // if (exitCount == 2)
    // {
      download_file.close();
    // }
  }
  
  
  return gwstatus;
}

#if 0
int AT_responseHandler(int curr, String datasend = "")
{
  SERIAL_MST("AT_responseHandler");
  String response = "";
  while (Serial2.available())
  {
    if (Serial2.available())
    {
      char ch = Serial2.read();
      response += ch;
    }
  }
  SERIAL_MST(response);
  if (curr == 9)
  {
    if (response.indexOf("ERROR") >= 0)
    {
      Serial2.print("AT+HTTPTERM\r\n");
      delay(1000);
      curr = 9;
      return curr;
    }
    else if (response.indexOf("OK") >= 0)
    {
      curr = 10;
      return curr;
    }
  }
  if (curr == 3)
  {
    int range = lowRange(response);
    if (range < 10)
    {
      curr = 0;
      return curr;
    }
  }
  if (curr == 12)
  {
    if (response.indexOf("200") >= 0)
    {
      AT_success = 1;
      delay(10);
      curr = 13;
      return curr;
    }
    else
    {
      Serial2.print("AT+HTTPACTION=1\r\n");
      AT_success = 0;
      delay(1000);
      curr = 15;
      return curr;
    }
  }
  if (response.indexOf("NO SERVICE") >= 0)
  {
    curr = 0;
  }
  if (response.indexOf("ERROR") >= 0)
  {
    curr = 0;
  }
  if (response.indexOf("OK") >= 0)
  {
    curr = curr + 1;
  }
  return curr;
}

int AT_downloadFile(String url, String filename)
{
  AT_success = 0;
  SERIAL_MST("SETTING UP THE MODULE..\n");
  delay(5000);
  int track = 0;
  delay(1000);
  while (1)
  {
    switch (track)
    {
    case 0: // AT+FSDEL=*.*
      Serial2.print("AT+FSDEL=*.*\r\n");
      delay(5000);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 1: // AT
      Serial2.print("AT\r\n");
      delay(500);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 2: // AT+CPIN?
      Serial2.print("AT+CPIN?\r\n");
      delay(1000);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 3: // AT+CSQ
      Serial2.print("AT+CSQ\r\n");
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 4: // AT+CREG?
      Serial2.print("AT+CREG?\r\n");
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 5: // AT+CGREG?
      Serial2.print("AT+CGREG?\r\n");
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 6: // AT+CPSI?
      Serial2.print("AT+CPSI?\r\n");
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 7: // AT+CGDCONT?
      Serial2.print("AT+CGDCONT?\r\n");
      delay(1000);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 8: // AT+CGACT?
      Serial2.print("AT+CGACT?\r\n");
      delay(1000);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 9: // AT+HTTPINIT
      Serial2.print("AT+HTTPINIT\r\n");
      delay(100);
      track = AT_responseHandler(track);
      delay(100);
      break;
    case 10: // AT+HTTPPARA="URL"
      Serial2.print("AT+HTTPPARA=\"URL\",\"" + url + "\"\r\n");
      delay(10);
      track = AT_responseHandler(track);
      delay(100);
      break;
    case 11: // AT+HTTPPARA="CONTENT"
      Serial2.print("AT+HTTPPARA=\"CONTENT\",\"application/x-www-form-urlencoded\"\r\n");
      delay(10);
      track = AT_responseHandler(track);
      delay(100);
      break;
    case 12: // AT+HTTPACTION
      Serial2.print("AT+HTTPACTION=1\r\n");
      delay(15000);
      track = AT_responseHandler(track);
      delay(1000);
      break;
    case 13: // AT+HTTPREADFILE
      Serial2.print("AT+HTTPREADFILE=\"" + filename + "\"\r\n");
      delay(3000);
      track = AT_responseHandler(track);
      delay(500);
      break;
    case 14: // AT+HTTPTERM
      Serial2.print("AT+HTTPTERM\r\n");
      delay(10);
      track = AT_responseHandler(track);
      delay(100);
      break;
    }
    if (track == 15)
    {
      SERIAL_MST("AT command sequence completed");
      break; // break while loop
    }
  }
  return AT_success;
}

#endif

int AT_POST_OTA(String url, String readFileCommand)
{
    delay(10000);

  int cfuncount = 0, poststatus = 0;
  String msgfrom4g = "";
  String authkey = readFile(LittleFS,"/authkey");
  String header_url = "AT+HTTPPARA=\"USERDATA\",secretkey:"+secretkey+"|OK|2000";
  String header_url1 = "AT+HTTPPARA=\"USERDATA\",authkey:"+authkey+"|OK|2000";


  //Serial2.print("AT+HTTPTERM\r\n");
  delay(3000);

  for (int i = 0; i < 8; i++)
  {
    if (i == 4)
    {
      msgfrom4g = Serial4gATcommands(header_url, "");
      msgfrom4g = Serial4gATcommands(header_url1, "");
      msgfrom4g = Serial4gATcommands(OTA_COMMANDS[i], "");

    }
    else if (i == 2)
    {
      msgfrom4g = Serial4gATcommands(url, "");
    }
    else if (i == 6)
    {
      msgfrom4g = Serial4gATcommands(readFileCommand, "");
    }
    else
    {
      msgfrom4g = Serial4gATcommands(OTA_COMMANDS[i], "");
    }

    //----------------------------------------------------------------------------------------------

    if (msgfrom4g.indexOf("error") >= 0)
    {
      CFUN();
      poststatus = 0;
      break;
    }
    else if (msgfrom4g.indexOf("200 OK") >= 0)
    {
      SERIAL_MST("200 RECEIVED");
      poststatus = 1;
    }
  }
  // SERIAL_MST(String(poststatus));
  return poststatus;
}


//int AT_POST_FILE(String data, String cftranrx, String url)
//{
//  delay(10000);
//
//  int cfuncount = 0, poststatus = 0;
//  String msgfrom4g = "";
//
//  // Serial2.print("AT+HTTPTERM\r\n");
//  // delay(3000);
//
//  for (int i = 0; i < 12; i++)
//  {
//    if (i == 3)
//    {
//      msgfrom4g = Serial4gATcommands(cftranrx, data);
//    }
//    else if (i == 6)
//    {
//      msgfrom4g = Serial4gATcommands(url, "");
//    }
//    else
//    {
//      msgfrom4g = Serial4gATcommands(AT_COMMANDS_POSTFILE[i], "");
//    }
//
//    //----------------------------------------------------------------------------------------------
//
//    if (msgfrom4g.indexOf("error") >= 0)
//    {
//      CFUN();
//      poststatus = 0;
//      break;
//    }
//    else if (msgfrom4g.indexOf("200 OK") >= 0)
//    {
//      SERIAL_MST("200 RECEIVED");
//      poststatus = 1;
//    }
//  }
//  // SERIAL_MST(String(poststatus));
//  return poststatus;
//}

int get4GFileSize(String response)
{
  int filesize = 0;
  String intr = "", final = "";
  intr = response.substring(response.indexOf(':') + 2);
  for (int i = 0; i < intr.indexOf('\n') - 1; i++)
  {
    final = final + intr[i];
  }
  final.trim();
  filesize = final.toInt();
  globalfsize = globalfsize + filesize;
  return filesize;
}

String getChunk(String cftrantx_response, int rem_bytes = 0)
{
  //     SERIAL_MST("getChunk");
  String chunk = "";
  int endpoint = cftrantx_response.length() - 22;
  int startpoint = 0;
  if (rem_bytes != 0)
  {
    startpoint = endpoint - rem_bytes;
    exitCount = exitCount + 1;
  }
  else
  {
    startpoint = endpoint - 320;
  }
  chunk = cftrantx_response.substring(startpoint, endpoint);
  // SERIAL_MST(chunk);
  return chunk;
}

int read4GFileSystem(String filename, File file)
{
  SERIAL_MST("read4GFileSystem");
  int i = 0, fsize = 0, start_byte = 0, num_loops = 0, rem_bytes = 0, status = 0, fileStatus = 1;
  String attri_response = "";
  Serial2.print("AT+FSATTRI=" + filename + "\r\n");
  delay(500);
  while (Serial2.available())
  {
    if (Serial2.available())
    {
      char ch = Serial2.read();
      attri_response += ch;
    }
  }
  fsize = get4GFileSize(attri_response);
  SERIAL_MST("File size to be transferred : " + String(fsize));
  SERIAL_MST("Reading 4G module File System\n");
  num_loops = (fsize / 320);
  rem_bytes = (fsize - (num_loops * 320));
  // SERIAL_MST(String(num_loops));
  // SERIAL_MST(String(rem_bytes));
  if (fsize != 0 && fsize < (LittleFS.totalBytes() - LittleFS.usedBytes()))
  {
    status = 1;
    for (int i = 0; i <= num_loops; i++)
    {
      String command = "", response = "";
      String chunk = "";
      SERIAL_MST("Progress : " + String((float)(start_byte * 100) / fsize) + "% complete");
      if (i == num_loops)
      {
        command = "AT+CFTRANTX=\"c:/" + filename + "\"," + String(start_byte) + "," + String(rem_bytes) + "\r\n";
      }
      else
      {
        command = "AT+CFTRANTX=\"c:/" + filename + "\"," + String(start_byte) + ",320\r\n";
      }
      Serial2.print(command);
      // SERIAL_MST("Command Sent : " + command);
      delay(40);
      while (Serial2.available())
      {
        if (Serial2.available())
        {
          char ch = Serial2.read();
          response = response + ch;
        }
      }
      // SERIAL_MST(response);
      if (i == num_loops)
      {
        chunk = getChunk(response, rem_bytes);
        if (file.print(chunk))
        {
          fileStatus = 1;
        }
        else
        {
          fileStatus = 0;
        }
      }
      else
      {
        chunk = getChunk(response);
        if (file.print(chunk))
        {
          fileStatus = 1;
        }
        else
        {
          fileStatus = 0;
        }
      }
      start_byte = start_byte + 320;
    }
  }
  else
  {
    SERIAL_MST("No file available to transfer/Space not available");
    status = 0;
  }
  if (fileStatus == 0 || status == 0)
  {
    return 0;
  }
  else
  {
    return 1;
  }
}

void gw_urlParser(String response)
{
  int k;
  String intr[6];
  int i = 0;
  for (int h = 0; h < 6; h++)
  {
    k = response.indexOf("\n");
    response = response.substring(k + 1, response.length());
    intr[i] = response;
    // SERIAL_MST("String is :" + response);
    i++;
  }
  SERIAL_MST("Intermediate string is:" + intr[3].substring(0, intr[3].length() - 1 - intr[4].length()) + "ok");
  String cmd_data_intr = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  // SERIAL_MST(cmd_data_intr);
  int temp = cmd_data_intr.indexOf(",");
  gw_otaurl[0] = cmd_data_intr.substring(0, temp);
  gw_otaurl[1] = cmd_data_intr.substring(temp + 1, cmd_data_intr.indexOf("\n"));
}

void node_urlParser(String response)
{
  int k;
  String intr[6];
  int i = 0;
  for (int h = 0; h < 6; h++)
  {
    k = response.indexOf("\n");
    response = response.substring(k + 1, response.length());
    intr[i] = response;
    // SERIAL_MST("String is :" + response);
    i++;
  }
  SERIAL_MST("Intermediate string is:" + intr[3].substring(0, intr[3].length() - 1 - intr[4].length()) + "ok");
  // nodeotaurl = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  String tempstr = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  SERIAL_MST(tempstr);
  if (tempstr.indexOf("1.0") >= 0)
  {
    SERIAL_MST("No OTA available for node");
  }
  else
  {
    nodeotaurl = tempstr;
  }
}

void writeCommandsIntoFile(String commands)
{
  int k;
  String intr[6];
  int i = 0;
  for (int h = 0; h < 6; h++)
  {
    k = commands.indexOf("\n");
    commands = commands.substring(k + 1, commands.length());
    intr[i] = commands;
    // SERIAL_MST("String is :" + commands);
    i++;
  }
  String cmd_data_intr = intr[3].substring(0, intr[3].length() - 1 - intr[4].length());
  SERIAL_MST("Command received = " + cmd_data_intr);
  cmd_data_intr.trim();
  if (cmd_data_intr != "0")
  {
    writeFile("/commandsfromserver", cmd_data_intr);
  }
  else
  {
    SERIAL_MST("NO COMMANDS!");
  }
}

/////////////////////get obs and scalar///////////////////

int GetFileListfromNode()
{
  String fileList = "";
  File root = LittleFS.open("/OBSC");
  if (!root)
  {
    SERIAL_MST("Failed to open directory");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("Not a directory");
    return 0;
  }

  File file = root.openNextFile();
  while (file)
  {
    fileList += String(file.name()) + ",";
    file = root.openNextFile();
  }
  file.close();
  root.close();
  
  if(fileList.length()>0)
  {
  divide(fileList);
  }
  return 1;
}

int divide(String payload)
{

  int num_files = 1;
  char filelist[2000] = {0};
  SERIAL_MST(payload);
  payload.toCharArray(filelist, 5000);

  char *filename = strtok(filelist, ",");

  while (filename != NULL)
  {
    // delay(1000);

    // SERIAL_MST("File name : " + String(filename));

    // SERIAL_MST("File Count is :" + String(num_files));
    num_files++;
    getfilefromnode(filename);
    filename = strtok(NULL, ",");
  }
  return 1;
}

void getfilefromnode(String fileid)
{
  String filedata = "";
  filedata = readFile(LittleFS, "/OBSC/" + fileid);

  delay(100);
  File file = LittleFS.open("/meterreading" + g_filename + String(fileCount));
  if (!file)
  {
    SERIAL_MST("Creating new file because last one was deleted");
    writeFile("/meterreading" + g_filename + String(fileCount), "");
  }
  int filesize = file.size();
  file.close();
  SERIAL_MST("Local File size : " + String(filesize));
  SERIAL_MST(filedata);
  filedata.trim();
  if(filedata.length() > 0)
  {
  if ((filesize + filedata.length()) < 25000)
  {
    appendFile_new(LittleFS, "/meterreading" + g_filename + String(fileCount), filedata);
    delay(1000);
    SERIAL_MST("MEMORY DETAILS : " + String(ESP.getFreeHeap()));

    deleteFile(LittleFS, "/OBSC/" + fileid);

    filedata = "";
  }
  else
  {
    fileCount = fileCount + 1;
    writeFile("/filenamecount", String(fileCount));
    String filename_l = "/completefile" + String(fileCount);

    SERIAL_MST(filename_l);
    writeFile("/meterreading" + filename_l, "");

    appendFile_new(LittleFS, "/meterreading" + filename_l, filedata);
    delay(1000);
    SERIAL_MST("MEMORY DETAILS : " + String(ESP.getFreeHeap()));

    deleteFile(LittleFS, "/OBSC/" + fileid);

    filedata = "";
    return;
  }
  }
}

//////////////////////////////get load and ip////////////////////

int GetIPLfromNode()
{
  String fileList = "";
  File root = LittleFS.open("/IPL");
  if (!root)
  {
    SERIAL_MST("Failed to open directory");
    return 0;
  }
  if (!root.isDirectory())
  {
    SERIAL_MST("Not a directory");
    return 0;
  }

  File file = root.openNextFile();
  while (file)
  {
    fileList += String(file.name()) + ",";
    file = root.openNextFile();
  }
  file.close();
  root.close();
  if(fileList.length()>0)
  {
  divideIPL(fileList);
  }
  return 1;
}

int divideIPL(String payload)
{

  int num_files = 1;
  char filelist[2000] = {0};
  SERIAL_MST(payload);
  payload.toCharArray(filelist, 5000);

  char *filename = strtok(filelist, ",");

  while (filename != NULL)
  {
    // delay(1000);

    // SERIAL_MST("File name : " + String(filename));

    // SERIAL_MST("File Count is :" + String(num_files));
    num_files++;
    getIPLfromnode(filename);
    filename = strtok(NULL, ",");
  }
  return 1;
}

void getIPLfromnode(String fileid)
{
  String filedata = "";
  filedata = readFile(LittleFS, "/IPL/" + fileid);

  delay(100);
  File file = LittleFS.open("/IPLreading" + g_filename + String(fileCount));
  if (!file)
  {
    SERIAL_MST("Creating new file because last one was deleted");
    writeFile("/meterreading" + g_filename + String(fileCount), "");
  }
  int filesize = file.size();
  file.close();
  SERIAL_MST("Local File size : " + String(filesize));
  SERIAL_MST(filedata);
  filedata.trim();
  if(filedata.length() > 0)
  {
  if ((filesize + filedata.length()) < 25000)
  {
    appendFile_new(LittleFS, "/IPLreading" + g_filename + String(fileCount), filedata);
    delay(1000);
    SERIAL_MST("MEMORY DETAILS : " + String(ESP.getFreeHeap()));

    deleteFile(LittleFS, "/IPL/" + fileid);

    filedata = "";
  }
  else
  {
    fileCount = fileCount + 1;
    writeFile("/IPLcount", String(fileCount));
    String filename_l = "/completefile" + String(fileCount);

    SERIAL_MST(filename_l);
    writeFile("/IPLreading" + filename_l, "");

    appendFile_new(LittleFS, "/IPLreading" + filename_l, filedata);
    delay(1000);
    SERIAL_MST("MEMORY DETAILS : " + String(ESP.getFreeHeap()));

    deleteFile(LittleFS, "/IPL/" + fileid);

    filedata = "";
    return;
  }
  }
}

////////////////////////////////////////////////////////////////////////


void getAndExecuteCommands()
{
  SERIAL_MST("getAndExecuteCommands");

  // get commands from server

  internetCommandReader();

  // divide commands

  String serverCommands = readFile(LittleFS, "/commandsfromserver");
  int numcommands = 0;
  // find the number of commands available
  char buf[serverCommands.length() + 1] = {0};
  serverCommands.toCharArray(buf, serverCommands.length() + 1);
  for (int i = 0; i < serverCommands.length(); i++)
  {
    if (buf[i] == ',')
    {
      numcommands++;
    }
  }
  if (serverCommands.length() > 1)
  {
    char *token = strtok(buf, ",");
    int i = 0;
    char *cmds[50];
    while (token != NULL)
    {
      cmds[i] = (token);
      token = strtok(NULL, ",");
      i++;
      if (i > numcommands)
      {
        break;
      }
    }

    // execute the commands
    for (int i = 0; i <= numcommands; i++)
    {
      SERIAL_MST("Command " + String(i) + " = " + String(cmds[i]));
      SERIAL_MST("Node code will run from here");
      CheckAndExecuteCommandsToNodes(String(cmds[i]));
    }
    // send status to server
    // clearingfailedcmds();
  }
  else
  {
    SERIAL_MST("no commands");
  }

  deleteFile(LittleFS, "/commandsfromserver"); // 17 feb modified by vaishnavi
}

void internetCommandReader()
{
  // clearingfailedcmds();

  int commandstatus = 0;
  int success = 0;
  SERIAL_MST(rtc.getTime("%A, %B %d %Y %H:%M:%S"));
  String imei = readFile(LittleFS , "/IMEI");
//  String url = "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/getcommands?imei=";
    String url = "AT+HTTPPARA=\"URL\",\"http://122.166.2.21:16006/getcommands?imei=";

  GWID.trim();
  if (imei.length() > 0)
  {
    url = url + imei +"&gwid="+GWID+ "\"" + "|OK|2000";
  }
  else
  {
    String macid = WiFi.macAddress();
    macid.replace(":", "");
    url = url + macid + "&gwid=" + GWID + "\"" + "|OK|2000";
  }

  for (int i = 0; i < 2; i++)
  {
    success = AT_GET(url);
    if (success == 1)
    {
      SERIAL_MST("------------------get success----------------");
      break;
    }
  }
  if (success == 1)
  {

    SERIAL_MST("-----------------getcommands success-----------------");
  }
}

void CreateNoresponseDataFile(String filedata, String Data)
{
  if(global_NodeID == "")
  {
    global_NodeID = "0";
  }
  char temp[5];
  String FinalInst_str = "$";
  FinalInst_str += global_NodeID;
  FinalInst_str += "_";
  FinalInst_str += 0; //(String)PhaseType;
  FinalInst_str += "_";
  FinalInst_str += "E";
  FinalInst_str += "_";
  FinalInst_str += "00"; // FinalInst_str
  FinalInst_str += "_";
  FinalInst_str += "00"; // METER MAKE
  FinalInst_str += "_";
  FinalInst_str += global_NodeID; // MeterSerialNo_Final;
  FinalInst_str += "_";

  FinalInst_str += filedata;
  FinalInst_str += "_";
  FinalInst_str += Data;
  FinalInst_str.trim();
//  FinalInst_str += "_";
  FinalInst_str += "$";

  String Inst_Data_FIle_With_BlockID = "";

  Inst_Data_FIle_With_BlockID = "/IPL"; // 13-04-2022
  Inst_Data_FIle_With_BlockID += "/";
  Inst_Data_FIle_With_BlockID += "00"; // BlockID
  Inst_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)rtc.getDay());
  Inst_Data_FIle_With_BlockID += "00";
  sprintf(temp, "%02s", (String)rtc.getMonth() + 1);
  Inst_Data_FIle_With_BlockID += "00";
  sprintf(temp, "%04s", (String)rtc.getYear());
  Inst_Data_FIle_With_BlockID += "00";
  Inst_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)rtc.getHour());
  Inst_Data_FIle_With_BlockID += "00";
  sprintf(temp, "%02s", (String)rtc.getMinute());
  Inst_Data_FIle_With_BlockID += "00";

  Inst_Data_FIle_With_BlockID += "_";
  Inst_Data_FIle_With_BlockID += "E.txt";

  seriallogger_string("Inst BlockID FILE NAME: " + Inst_Data_FIle_With_BlockID);
  // seriallogger_string("\r\n");

  WritePostDataIntoBlockIDFile(Inst_Data_FIle_With_BlockID, FinalInst_str); // 88888888
                                        // ReadFromFile(Inst_Data_FIle_With_BlockID);
}

void ota_blinker(int pinNumber, int loopNumber)
{
  for (int i = 0; i < loopNumber; i++)
  {
    digitalWrite(pinNumber, HIGH);
    delay(300);
    digitalWrite(pinNumber, LOW);
    delay(300);
  }
}

bool ReadEventProfileData(int EventType)
{
  int load_res_count = 0;
  bool load_response = false;
  int retvalue = 0;

  while(!load_response)
  {
    retvalue = ProfileRead(EventType);

    if(retvalue == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }
  

  if (retvalue == 1)
  {
    return CreateIPLDataFile(EventType, rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());
  }
  else
  {
    return false;
  }
}



int ProfileRead(char MType)
{
  int value = 1;
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  char MeterDataType = MType;
  // char MeterDataType = EVENTPOWER;
  bool frame_complete = true;
  int response_count = 0;
  special_counter = 0;
  global_frame = "";
  int mx_res_count = 0;

  int total_rowcount = 0;
  int dummy_rowcount = 0;
  int t_array_size = 0;
  int billing_index = 0;
  int param_list_count = 0;
  int temp_param_length = 0;
  int max_param_length = 0;
  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  SerialRead(arrindex, ResByteCount);
  // seriallogger_string("READ AARQ");

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  if ((ResponseBuffer[arrindex][25] == 0x03 && ResponseBuffer[arrindex][26] == 0x02 && ResponseBuffer[arrindex][27] == 0x01 && ResponseBuffer[arrindex][28] == 0x00) ||
      (ResponseBuffer[arrindex][29] == 0x03 && ResponseBuffer[arrindex][30] == 0x02 && ResponseBuffer[arrindex][31] == 0x01 && ResponseBuffer[arrindex][32] == 0x00))
  {
//    CreateNoresponseDataFile("20", "METER INSTANT SUCCESS");
  }
  else
  {
//    CreateNoresponseDataFile("21", "METER INSTANT FAILURE");
    return 0;
  }

  // 04-04-2022
  GetSequenceNumber(0);


    special_counter = 0;

    MeterCommandFrame(Fromdate, Todate, MeterDataType);

    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);



    ResByteCount = 0;

    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();

    if (METER_DEBUG == TRUE)
    {
      // Serial2.println();
      Serial2.print("SPECIAL TX : ");
      for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][i], HEX);
        Serial2.print(" ");
      }
    Serial2.println();

    }


    SerialRead(arrindex, ResByteCount);

    // BREAK METER READING OF NO RESPONSE FROM METER
    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");

      return 0;
    }
    // global_frame = profile_pe_count ;
    // for(int c = 0; c < LoadREQframeptr[arrindex][2] + 2; c++)
    // {
    //   global_frame  = global_frame + String(LoadREQframeptr[arrindex][c], HEX);
    //   global_frame = global_frame + " ";
    // }
    int temp_buff_size = 0;
    if (ResponseBuffer[arrindex][1] == 0xA1)
    {
      temp_buff_size = 256;
    }
    else if (ResponseBuffer[arrindex][1] == 0xA2)
    {
      temp_buff_size = 512;
    }
    for (int c = 0; c < (ResponseBuffer[arrindex][2] + 2 + temp_buff_size); c++)
    {
      global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
      global_frame = global_frame + " ";
    }
    global_frame.trim();
    /*****************************************************************************************/
    while (ResponseBuffer[arrindex][1] == 0xA8) // first frame //unlimite loop
    {
      if(mx_res_count >= COUNT_LP)
      {
          seriallogger_string("While count break : " +String(mx_res_count));
          break;
      }
      FrameType = SUPERVISORY_FRAME;
      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(++arrindex, LoadREQframeptr);

      ResByteCount = 0;

      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      SerialRead(arrindex, ResByteCount);

      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");

        return 0;
      }
      global_frame = global_frame + "_";
      for (int c = 0; c < ResponseBuffer[arrindex][2] + 2; c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }
      global_frame.trim();
      seriallogger_string("While count : "+String(mx_res_count));
      mx_res_count++;
    }

    if (METER_MAKE == EEPL && MeterDataType == EVENTPOWER)
    {
      FrameType = SPECIAL_FRAME;
      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(++arrindex, LoadREQframeptr);

      ResByteCount = 0;
      if (METER_DEBUG == TRUE)
      {
        // Serial2.println();
        Serial2.print("SPECIAL TX : ");
        for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
        {
          Serial2.print(LoadREQframeptr[arrindex][i], HEX);
          Serial2.print(" ");
        }
        Serial2.println();
    
      }

      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      SerialRead(arrindex, ResByteCount);

      // BREAK METER READING OF NO RESPONSE FROM METER
      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");
        return 0;
      }
      global_frame = global_frame + "_";
      for (int c = 0; c < (ResponseBuffer[arrindex][2] + 2 + temp_buff_size); c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }
      global_frame.trim();

    }
    /*****************************************************************************************/
  

  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  // delay(1000);
  SerialRead(arrindex, ResByteCount);
  // seriallogger_string("READ DISC");

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;

  return 1;
}

bool ProfileFilecreate(char MType, int Load_ChoppedByteCount, int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year) // added arg_month on 16-06-2022 //added arg_year on 18-06-2022
{
  char temp[5] = {0};
  String Load_Data_FIle_With_BlockID = "";
  String FinalLoad_str = "$";
  char temp_BlockID[5] = {0};
  sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
  FinalLoad_str += global_NodeID;
  FinalLoad_str += "_";
  FinalLoad_str += (String)meter_type;
  FinalLoad_str += "_";

  if(MType == LOAD_PROFILE_DATA)
  {
  FinalLoad_str += "L";
  }
  else if(MType == LOAD_PROFILE_SCALAR)
  {
    FinalLoad_str += "LPSV";
  }
  else if(MType == LOAD_DATA_OBIS)
  {
    FinalLoad_str += "LPOB";
  }
  else if(MType == LOAD_SCALAR_OBIS)
  {
    FinalLoad_str += "LSOB";
  }
  else if(MType == INSTANTSCALAR)
  {
    FinalLoad_str += "IPSV";
  }
  else if(MType == INSTANT_DATA_OBIS)
  {
    FinalLoad_str += "IPOB";
  }
    else if(MType == INSTANT_SCALAR_OBIS)
  {
    FinalLoad_str += "ISOB";
  }
  else if(MType == BILLINGSCALAR)
  {
  FinalLoad_str += "BSV";
  }
  else if(MType == BILLING_DATA_OBIS)
  {
    FinalLoad_str += "BOB";
  }
    else if(MType == BILLING_SCALAR_OBIS)
  {
    FinalLoad_str += "BSOB";
  }
  else if(MType == EVENT_SCALAR)
  {
    FinalLoad_str += "ESV";
  }
  else if(MType == EVENT_DATA_OBIS)
  {
    FinalLoad_str += "EOB";
  }
  else if(MType == EVENT_SCALAR_OBIS)
  {
    FinalLoad_str += "ESOB";
  }
    else if(MType == DL_SCALAR_DATA)
  {
    FinalLoad_str += "DLS";
  }
  else if(MType == DAILY_LOAD_OBIS)
  {
    FinalLoad_str += "DLOB";
  }
  else if(MType == DL_SCALAR_OBIS)
  {
    FinalLoad_str += "DSOB";
  }

  FinalLoad_str += "_";
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  FinalLoad_str += MeterSerialNo_Final;
  FinalLoad_str += "_";

  FinalLoad_str += global_frame;
  FinalLoad_str.trim();
  FinalLoad_str += "$";
  
  Load_Data_FIle_With_BlockID = "/OBSC"; // 13-04-2022
  
  Load_Data_FIle_With_BlockID += "/";

  sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)arg_month);
  Load_Data_FIle_With_BlockID += temp;
  // sprintf(temp, "%04s", (String)arg_year);
  // Load_Data_FIle_With_BlockID += temp;
  Load_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)g_hours);
  Load_Data_FIle_With_BlockID += temp;

  // if (METER_MAKE == LT)
  sprintf(temp, "%02s", (String)arg_minute);
  // else
  //   sprintf(temp, "%02s", (String)rtc.getMinute());

  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  if(MType == BILLINGSCALAR)
  {
  Load_Data_FIle_With_BlockID += "BSV.txt";  
  }
  else if(MType == LOAD_PROFILE_DATA)
  {
  Load_Data_FIle_With_BlockID += "L.txt";
  }
  else if(MType == INSTANTSCALAR)
  {
    Load_Data_FIle_With_BlockID += "IPSV.txt";
  }
  else if(MType == LOAD_PROFILE_SCALAR)
  {
    Load_Data_FIle_With_BlockID += "LPSV.txt";
  }
  else if(MType == LOAD_DATA_OBIS)
  {
    Load_Data_FIle_With_BlockID += "LPOB.txt";
  }
  else if(MType == LOAD_SCALAR_OBIS)
  {
    Load_Data_FIle_With_BlockID += "LSOB.txt";
  }
  else if(MType == INSTANT_DATA_OBIS)
  {
    Load_Data_FIle_With_BlockID += "IPOB.txt";
  }
  else if(MType == INSTANT_SCALAR_OBIS)
  {
    Load_Data_FIle_With_BlockID += "ISOB.txt";
  }
  else if(MType == BILLING_DATA_OBIS)
  {
    Load_Data_FIle_With_BlockID += "BOB.txt";
  } 
  else if(MType == BILLING_SCALAR_OBIS)
  {
    Load_Data_FIle_With_BlockID += "BSOB.txt";
  }
  else if(MType == EVENT_SCALAR_OBIS)
  {
    Load_Data_FIle_With_BlockID += "ESOB.txt";
  }
  else if(MType == EVENT_SCALAR)
  {
    Load_Data_FIle_With_BlockID += "ESV.txt";
  }
  else if(MType == EVENT_DATA_OBIS)
  {
    Load_Data_FIle_With_BlockID += "EOB.txt";
  }
    else if(MType == DL_SCALAR_DATA)
  {
    Load_Data_FIle_With_BlockID += "DLS.txt";
  }
  else if(MType == DAILY_LOAD_OBIS)
  {
    Load_Data_FIle_With_BlockID += "DLOB.txt";
  }
  else if(MType == DL_SCALAR_OBIS)
  {
    Load_Data_FIle_With_BlockID += "DSOB.txt";
  }

  seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);

  seriallogger_string("insta obis: " + FinalLoad_str);
  WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);

  // Serial.print(String(FinalLoad_str));
  // Version 3
  // Code to validate whether data has been written into file properly
  String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);

  if (temp_load_data_string_for_validation.startsWith("$"))
  {
    temp_load_data_string_for_validation.trim();
    if (temp_load_data_string_for_validation.endsWith("$"))
      return true;
    else
    {
      LittleFS.remove(Load_Data_FIle_With_BlockID);
      return false;
    }
  }
  else
  {
    LittleFS.remove(Load_Data_FIle_With_BlockID);
    return false;
  }
}


int ParseMeterDT_DATA(byte kWhValue[])
{
  int index = 0;
  unsigned int ddoublelongvalue = 0;
  // float kWh_finalvalue = 0, kWh_floatvalue = 0;;
  if (kWhValue[index] == DT_DOUBLE_LONG || kWhValue[index] == DT_DOUBLE_LONG_UNSIGNED)
  {
    index++;
    while (index < (sizeof(int) + 1))
    {
      ddoublelongvalue = (ddoublelongvalue << 8) | kWhValue[index++];
    }
  }
  else if (kWhValue[index] == 0x12)
  {
    index++;
    while (index < (sizeof(short) + 1))
    {
      ddoublelongvalue = (ddoublelongvalue << 8) | kWhValue[index++];
    }
  }
  return ddoublelongvalue;
}

int WiFi_downloadFile()
{

  int return_val = 0;
  WiFi.begin("gatewayfwupdate", "Krishna_12");
  int startTime = millis();
  while (WiFi.status() != WL_CONNECTED && (millis() - startTime) <= 20000)
  { // Wait for the WiFI connection completion
    delay(500);
    SERIAL_MST("Waiting for connection");
  }
  if ((WiFi.status() == WL_CONNECTED)) // Check the current connection status
  {
    HTTPClient http; // CREATING INSTANCE OF HTTP
    int newversion_found = 0;
    String new_firmware_url = "";
    // check if new version is available to download or not.
    http.begin("http://configurations.ms-tech.in:9838/getlatestgwversion_4gnode?gwid=" + GWID + "&cv=" + String(gw_current_firmware_version));
    int httpCode = http.GET();
    SERIAL_MST(String(httpCode));
    if (httpCode > 0)
    {
      if (httpCode == HTTP_CODE_OK) // Check for the returning code
      {
        String payload = http.getString();
        SERIAL_MST(payload);
        float newVersion = payload.toFloat();
        if (newVersion != 1.00)
        {
          new_firmware_url = payload;
          SERIAL_MST("new version found");
          newversion_found = 1;
        }
        else
        {
          SERIAL_MST("Firmware is uptodate");
          http.end();
          return_val = 0;
          return return_val;
        }
      }
    }
    http.end();
    writeFile("/download.bin", "");
    File file = LittleFS.open("/download.bin", "w");
    // file.seek(0,SeekEnd);
    HTTPClient http2;
    if (file)
    {
      SERIAL_MST("Downloading file");
      // http.begin( "http://172.104.244.42/builds/1.1/OTA_FILE_TESTING.ino.esp32.bin");       // GETTING FILE FROM SERVER
      // http2.begin("http://172.104.244.42/builds/1.3/gateway_code_with_fixed_file_function.ino.esp32.bin");
      new_firmware_url.trim();

      SERIAL_MST(new_firmware_url);
      http2.begin(new_firmware_url);
      int httpCode2 = http2.GET();
      SERIAL_MST(String(httpCode2));
      if (httpCode2 > 0)
      {
        if (httpCode2 == HTTP_CODE_OK) // Check for the returning code
        {
          SERIAL_MST("Hello");
          http2.writeToStream(&file);
          return_val = 1;
        }
        else
        {
          SERIAL_MST("[HTTP] GET... failed, error: " + String(http2.errorToString(httpCode2).c_str()));
          // firmware = 0;
          return_val = 0;
        }
      }
      else
      {
        SERIAL_MST("Invalid HTTP code");
        return_val = 0;
      }

      SERIAL_MST("you have finished downloading");
      SERIAL_MST(String(file.size()));
      
      file.close();
        
            
        
    }
    else
    {
      SERIAL_MST("File not present");
      return_val = 0;
    }
    http2.end();
    // firmware = 1;
  }

  else
  {
    SERIAL_MST("WIFI not Connected !!!!");
    return_val = 0;
  }

WiFi.disconnect();

  return return_val;
}

void handleupdatefirmwareWIFI()
{
  SERIAL_MST("\nSearch for firmware..");
  File firmware = LittleFS.open("/download.bin", "r");
  SERIAL_MST(String(firmware.size()));
  if (firmware)
  {
    SERIAL_MST(F("found!"));
    SERIAL_MST(F("Try to update!"));
    Update.onProgress(progressCallBack);
    Update.begin(firmware.size(), U_FLASH);
    Update.writeStream(firmware);
    if (Update.end())
    {
      SERIAL_MST(F("Update finished!"));
      // SERIAL_MST(millis());
      ESP.restart();
    }
    else
    {
      SERIAL_MST(F("Update error!"));
      SERIAL_MST(String(Update.getError()));
    }
    // Updateflag = 1;
    firmware.close();
  }
  else
  {
    SERIAL_MST(F("Not found!"));
  }
}

void send_disconnect_command_to_serial(void)
{
 char DisconnectFrame[9]={0x7E,0xA0,0x07,0x03,0x41,0x53,0x56,0xA2,0x7E};
 Serial.write(&DisconnectFrame[0], (DisconnectFrame[2]+2));
  
 Serial.flush();
       if (METER_DEBUG == TRUE)
     {
       for(int i=0 ; i<(DisconnectFrame[2]+2);i++)
       {
       Serial2.print(DisconnectFrame[i], HEX);
       Serial2.print(" ");
       }
   }
  
  SerialRead(0, 0);
  delay(1000);
}

String httpPost(String host, String url)
{
  String payload = "";

  String serverPath = host + url;
  SERIAL_MST(serverPath);

  HTTPClient http2;
  http2.setTimeout(20000);
  http2.begin(serverPath.c_str());
  http2.addHeader("Content-Type", "application/json");

  String ble_data = GWID + " : RESETTING THE MODULE / RESTARTING THE ESP";
  // String encoded = base64::encode(ble_data);

  String payload2 = "{\"data2\":\"" + ble_data + "\",\"gwid\":\"" + GWID + "\"}";
  SERIAL_MST(payload2);

  int httpResponseCode = http2.POST(payload2); // Send HTTP GET request

  if (httpResponseCode == 200)
  {
    SERIAL_MST("HTTP Response code: ");
    SERIAL_MST(String(httpResponseCode));

    String payload = http2.getString();

    SERIAL_MST(String(payload.length()));

    http2.end();
    writeFile("/getlogs", "");
    SERIAL_MST("Data posted to server");
    return payload;
  }

  else
  {
    SERIAL_MST("Error code: ");

    SERIAL_MST(String(httpResponseCode));
    http2.end(); // Free resources
    return "error";
  }
}

void readonetime()
{
  if (checkforDirectory("/MeterSlNo", 3) == 0)
  {
    createDir(LittleFS, "/MeterSlNo");
  }  



  MeterSerialNo_Final = "";
  MeterSerialNo_Final = ReadMSNFromFile("/MeterSlNo/MSN.txt");
  MeterSerialNo_Final.trim();

  if (MeterSerialNo_Final == "NILL" || MeterSerialNo_Final == "")
      {
        read_meter_Data();
        esp_task_wdt_reset();
      }
}

void FormatNode()
{
  SERIAL_MST("FORMATING NODE");
  LittleFS.format();
  delay(20000);
  SERIAL_MST("TOTAL AVAILABLE MEMORY " +String(LittleFS.totalBytes() - LittleFS.usedBytes()));
  hardReset();
  
}

String node_serialization_4G(int build_id)
{
  int success = 0;
  File file = LittleFS.open("/NodeID/NodeID.txt", "r");
  String macaddr = WiFi.macAddress();
//  String url = "http://172.104.244.42:9838/getssidfrommac_v4g?buildid=" + String(build_id) + "&mac=" + macaddr;
  String payload;
  String nodedata = "0";
   String url = "AT+HTTPPARA=\"URL\",\"https://api.ms-tech.in/v2/getssidfrommac_v4g?buildid=" + String(build_id) + "&mac=" + macaddr + "\"" + "|OK|2000";
      SERIAL_MST(url);

  
  if (!file)
  {
    createDir(LittleFS, "/NodeID");
    for (int i = 0; i < 2; i++)
          {
            success = AT_GET(url);
            if (success == 1)
            {
              SERIAL_MST("------------------get success----------------");
              break;
            }
          }
          
    }
  else
  {
    file.close();
  }
  nodedata = readFile(LittleFS, "/NodeID/NodeID.txt");

return nodedata;
      
}

int testingRS232(void)
{
    int rs232Status = 0;
    int is_4g_ready = 0, datastatus = 0;
    WiFi.begin("Airtel_9986025401", "air72052");
    int retryCount=0;
    while (WiFi.status() != WL_CONNECTED)
    {
      delay(1000);
      if (retryCount == 10)
      {
        break;
      }
      retryCount++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
      int blinkcount = 0;
      Serial2.println("waiting for 5 sec");
      delay(5000);
      char SNRM[9]={0x7E, 0xA0, 0x07, 0x03, 0x41, 0x93, 0x5A, 0x64, 0x7E};
      Serial.write(&SNRM[0], (SNRM[2]+2));
      Serial.flush();
      SerialRead(0, 0);
      delay(1000);
      return_value = check_responsebuffer(0);
      if(return_value !=1)
      {
        blinkcount = blinkcount+1;
      }
      char DisconnectFrame[9]={0x7E,0xA0,0x07,0x03,0x41,0x53,0x56,0xA2,0x7E};
      Serial.write(&DisconnectFrame[0], (DisconnectFrame[2]+2));
      Serial.flush();
      SerialRead(0, 0);
      delay(1000);

      int statusofdir = checkforDirectory("/testreading", 3);
      if (statusofdir == 0)
      {
        createDir(LittleFS, "/testreading");
      }


      return_value = check_responsebuffer(0);
      if(return_value !=1)
      {
        blinkcount = blinkcount+1;
      }
      if(blinkcount == 2)
      {
        Serial.println();
        Serial.println("RS232 Test Success , Please check LED");
         digitalWrite(RS232_INDICATOR, HIGH);
         delay(5000);
//        digitalWrite(DATA_COMMUNICATION, HIGH);
//        delay(5000);
//        digitalWrite(DATA_COMMUNICATION, LOW);
        writeFile("/testreading/rs232test.txt","RS232_Test_Success");
        rs232Status = 1;
      }
      else
      {
        Serial.println();
        digitalWrite(RS232_INDICATOR, LOW);
        Serial.println("RS232 Test Failed");
        writeFile("/testreading/rs232test.txt","RS232_Test_Failed");

      }
      if(METER_DEBUG != TRUE)
      {
      is_4g_ready = basicATcommands();
      if (is_4g_ready)
      {
        datastatus = postNodeTestingData();
      }
      else
      {
        SERIAL_MST("Module not ready");
      }
    }
    }

    Serial.println("is_4g_ready stauts" + String(is_4g_ready));
    Serial.println("datastatus" + String(datastatus));
    Serial.println("rs232Status" + String(rs232Status));
    
  return rs232Status;
}


int getframelenth( unsigned char x_high, unsigned char x_low)
{
  int combined;
  combined = x_high;              //send x_high to rightmost 8 bits
  combined = combined<<8;         //shift x_high over to leftmost 8 bits
  combined |= x_low;              //logical OR keeps x_high intact in combined and fills in rightmost 8 bits   
  combined &= 0x07FF;             //move 5 byte to get length
  // if(METER_DEBUG == TRUE)
  // {
  // //  Serial2.println();
  // //  Serial2.print("x_high " + String(x_high));
  // //  Serial2.print("x_low " + String(x_low));
  // //  Serial2.print("temp_buff_size " + String(combined));
  // }
  
  return combined;
}

void readblockload()
{
  Serial2.println("in read load : ");

  bool load_response = false;
  int load_res_count = 0;
  int Load_ChoppedByteCount = 0;
  char fromDateTime[14] = {""};
  char ToDateTime[14] = {""};
  // WritePostDataIntoBlockIDFile("/ReadFulldayLoad.txt","07072023");
  String datetoreadload = ReadMSNFromFile("/ReadFulldayLoad.txt");
  Serial2.println(datetoreadload);
  String datefrom = "0000"+datetoreadload;
  String dateto = "2359"+datetoreadload;
  datefrom.toCharArray(fromDateTime,15);
  dateto.toCharArray(ToDateTime,15);


  while(!load_response)
  {
    Load_ChoppedByteCount = read_profileforload(LOAD_PROFILE_DATA, fromDateTime, ToDateTime,rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

}

void readdailyload()
{
  Serial2.println("in read daily load : ");

  bool load_response = false;
  int load_res_count = 0;
  int Load_ChoppedByteCount = 0;
  char fromDateTime[14] = {""};
  char ToDateTime[14] = {""};
  // WritePostDataIntoBlockIDFile("/ReadFulldayLoad.txt","07072023");
  // String datetoreadload = ReadMSNFromFile("/ReadFulldayLoad.txt");
  // Serial2.println(datetoreadload);
  // String datefrom = "0000"+datetoreadload;
  // String dateto = "2359"+datetoreadload;
  // datefrom.toCharArray(fromDateTime,15);
  // dateto.toCharArray(ToDateTime,15);

  String datefrom = "000018072023";
  String dateto = "000018072023";
  datefrom.toCharArray(fromDateTime,15);
  dateto.toCharArray(ToDateTime,15);


  while(!load_response)
  {
    Load_ChoppedByteCount = read_profileforload(DAILY_LOAD_DATA,fromDateTime, ToDateTime,rtc.getDay(), rtc.getHour(), rtc.getMinute(), rtc.getMonth() + 1, rtc.getYear());

    if(Load_ChoppedByteCount == 1 || load_res_count > 2)
    {
      load_response = true;
    }
    else
    {
      load_res_count++;
    }
  }

}


int read_profileforload(int mtype,char fromDateTime[], char ToDateTime[],int arg_loadday, int arg_BlockID, int arg_minute, int arg_month, int arg_year )
{
  
  //char LoadREQframeptr[30][MAX_SIZE] = {0};
  int ResByteCount = 0;
  int ChoppedByteCount = 0;
  int local_i = 0;
  int arrindex = 0;
  char Load_dis_con = 0;
  // char MeterDataType = LOAD_PROFILE_DATA;
  char MeterDataType = mtype;

  bool frame_complete = false;
  // int total_rowcount = 0;
  // int dummy_rowcount = 0;
  // int t_array_size = 0;
  int response_count = 0;
  bool Block_response = false;
  bool final_block = false;

  int segment_action = 0;
  int frame_size = 0;
  int mx_res_count = 0;
///////////////////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////////////////////
// MeterSerialNo_Final = "123989";
  char temp[5] = {0};
  String Load_Data_FIle_With_BlockID = "";
  String FinalLoad_str = "$";
  char temp_BlockID[5] = {0};
  sprintf(temp_BlockID, "%02s", (String)arg_BlockID /*g_day*/);
  FinalLoad_str += global_NodeID;
  FinalLoad_str += "_";
  FinalLoad_str += (String)meter_type;
  FinalLoad_str += "_";
  
  if(meter_type == LOAD_PROFILE_DATA)
    FinalLoad_str += "L";
  else
    FinalLoad_str += "DL";

  FinalLoad_str += "_";
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  sprintf(temp_BlockID, "%02s", (String)METER_MAKE /*g_day*/);
  FinalLoad_str += temp_BlockID;
  FinalLoad_str += "_";
  FinalLoad_str += MeterSerialNo_Final;
  FinalLoad_str += "_";

  Load_Data_FIle_With_BlockID = "/IPL"; // 13-04-2022
  
  Load_Data_FIle_With_BlockID += "/";

  sprintf(temp, "%02s", (String)arg_BlockID /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  sprintf(temp, "%02s", (String)arg_loadday /*g_day*/);
  Load_Data_FIle_With_BlockID += temp;
  sprintf(temp, "%02s", (String)arg_month);
  Load_Data_FIle_With_BlockID += temp;
  // sprintf(temp, "%04s", (String)arg_year);
  // Load_Data_FIle_With_BlockID += temp;
  Load_Data_FIle_With_BlockID += "_";
  sprintf(temp, "%02s", (String)g_hours);
  Load_Data_FIle_With_BlockID += temp;

  // if (METER_MAKE == LT)
  sprintf(temp, "%02s", (String)arg_minute);
  // else
  //   sprintf(temp, "%02s", (String)rtc.getMinute());

  Load_Data_FIle_With_BlockID += temp;

  Load_Data_FIle_With_BlockID += "_";

  if (mtype == LOAD_PROFILE_DATA)
    Load_Data_FIle_With_BlockID += "L.txt"; 
  else
    Load_Data_FIle_With_BlockID += "DL.txt"; 

  
  seriallogger_string("Load BlockID FILE NAME: " + Load_Data_FIle_With_BlockID);
  FinalLoad_str.trim();
  // WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, "{\"data2\":\"");
  WritePostDataIntoBlockIDFile(Load_Data_FIle_With_BlockID, FinalLoad_str);
 
/////////////////////////////////////////////////////////////////////////////////////////////////    

  memsetbuffer(AARQFrame, sizeof(AARQFrame));

  memsetbuffer(Fromdate, sizeof(Fromdate)); // 06-07-2022
  memsetbuffer(Todate, sizeof(Todate));   // 06-07-2022

  ClearResponseBuffer(); // Version 5 added on 29-06-2022 to clear the ResponseBuffer before starting meter reading.

  SNRMframing();
  hdlc_SendPacket(arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }

  SerialRead(arrindex, ResByteCount);

  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  arrqframe_index = AARQ_Client_Meter_Reader_Password(/*passwordkey*/);
  char FrameType = INFORMATION_FRAME;
  HdlcWrapperEncoding(FrameType, &AARQFrame[0], arrqframe_index);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();

  if (METER_DEBUG == TRUE)
  {
    Serial2.println();
    Serial2.print("Req : ");
    Serial2.print(arrindex);
    Serial2.print(" ");
    for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
      Serial2.print(" ");
    }
  }
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }


  if ((ResponseBuffer[arrindex][25] == 0x03 && ResponseBuffer[arrindex][26] == 0x02 && ResponseBuffer[arrindex][27] == 0x01 && ResponseBuffer[arrindex][28] == 0x00) ||
      (ResponseBuffer[arrindex][29] == 0x03 && ResponseBuffer[arrindex][30] == 0x02 && ResponseBuffer[arrindex][31] == 0x01 && ResponseBuffer[arrindex][32] == 0x00))
  {
//    CreateNoresponseDataFile("20", "METER INSTANT SUCCESS");
  }
  else
  {
//    CreateNoresponseDataFile("21", "METER INSTANT FAILURE");
    return 0;
  }

    GetSequenceNumber(0);
    
    DateTimeRange(Fromdate, Todate, fromDateTime, ToDateTime);

    global_frame = "";
    special_counter = 0;
    response_count = 0;
    MeterCommandFrame(Fromdate, Todate, MeterDataType);
    // 04-04-2022
    GetSequenceNumber(0);

    hdlc_SendPacket(++arrindex, LoadREQframeptr);

    ResByteCount = 0;



    Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
    Serial.flush();
    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("TX : ");
      for (int temp_i = 0; temp_i < LoadREQframeptr[arrindex][2] + 2; temp_i++)
      {
        Serial2.print(LoadREQframeptr[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
      Serial2.println();

    }
    SerialRead(arrindex, ResByteCount);
    
    int temp_buff_size = 0;
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

    if (METER_DEBUG == TRUE)
    {
      Serial2.println();
      Serial2.print("RX : ");
      for (int temp_i = 0; temp_i < temp_buff_size + 2; temp_i++)
      {
        Serial2.print(ResponseBuffer[arrindex][temp_i], HEX);
        Serial2.print(" ");
      }
    }

    // BREAK METER READING OF NO RESPONSE FROM METER
    if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
    {
      seriallogger_string("NO REPONSE/INVALID RESPONSE");
      return 0;
    }

    temp_buff_size = 0;
    temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);
    //Serial2.print("temp_buff_size" + String(temp_buff_size));

    for (int filedata = 0; filedata < (temp_buff_size + 2); filedata++)
    {
      global_frame = global_frame + String(ResponseBuffer[arrindex][filedata], HEX);
      global_frame = global_frame + " ";
    }
    global_frame.trim();

    appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,global_frame);

    if (ResponseBuffer[arrindex][11] == 0xC4)
    {
      if (ResponseBuffer[arrindex][12] == 0x02)
      {
        Block_response = true;
      }
       else if(ResponseBuffer[arrindex][12] == 0x01)
      {
        Block_response = false;
      }
    }



    segment_action = bitRead(ResponseBuffer[arrindex][1],3);
    
    if (Block_response == false && segment_action == 0)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 0 && ResponseBuffer[arrindex][14] == 0x01)
    {
      frame_complete = false;
    }
    else if(Block_response == true && segment_action == 1 && ResponseBuffer[arrindex][14] == 0x00)
    {
      frame_complete = true;
    }
    else
    {
      frame_complete = true;
    }

    /*****************************************************************************************/
    while (frame_complete) // first frame
    {
      if(mx_res_count >= COUNT_BILL)
      {
          seriallogger_string("While count break : " +String(mx_res_count));
          break;
      }
        segment_action = bitRead(ResponseBuffer[arrindex][1],3);

        if (segment_action == 0x00) //A0
        {
          response_count++;
          FrameType = SPECIAL_FRAME;
        }
        else
        {
          FrameType = SUPERVISORY_FRAME;
        }
      
      HdlcWrapperEncoding(FrameType, NULL, 0);
      GetSequenceNumber(0);
      hdlc_SendPacket(arrindex, LoadREQframeptr);

      ResByteCount = 0;

      Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
      Serial.flush();

      if (METER_DEBUG == TRUE)
      {
        // Serial2.println();
        Serial2.print("SUPER TX : ");
        for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
        {
          Serial2.print(LoadREQframeptr[arrindex][i], HEX);
          Serial2.print(" ");
        }
       Serial2.println();

      }

      SerialRead(arrindex, ResByteCount);

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);

      if (METER_DEBUG == TRUE)
      {
        Serial2.println();
        // Serial2.print("temp_buff_size " + String(temp_buff_size));
        Serial2.print("RX : ");
        for (int temp_i = 0; temp_i < temp_buff_size + 2; temp_i++)
        {
          Serial2.print(ResponseBuffer[arrindex][temp_i], HEX);
          Serial2.print(" ");
        }
      }

      // BREAK METER READING OF NO RESPONSE FROM METER
      if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
      {
        seriallogger_string("NO REPONSE/INVALID RESPONSE");
        frame_complete = false;
        return 0;
      }
//      global_frame = "";
      global_frame = "_";

      temp_buff_size = getframelenth(ResponseBuffer[arrindex][1],ResponseBuffer[arrindex][2]);
      Serial2.print("temp_buff_size" + String(temp_buff_size));

      for (int c = 0; c < temp_buff_size + 2; c++)
      {
        global_frame = global_frame + String(ResponseBuffer[arrindex][c], HEX);
        global_frame = global_frame + " ";
      }

      global_frame.trim();
      

      appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,global_frame);

      segment_action = bitRead(ResponseBuffer[arrindex][1],3);

      if(Block_response == false)
      {
        if (segment_action == 0x00)
        {
          frame_complete = false;
        }
      }
      else if(Block_response == true && final_block == false)
      {
        if (ResponseBuffer[arrindex][13] == 0xC1 && ResponseBuffer[arrindex][14] == 0x01)
        {
          if(segment_action == 0x00)
          {
            frame_complete = false;
          }
          else
          {
            final_block = true;
          }
        }
      }
      else if(final_block == true)
      {
        if (segment_action == 0x00)
        {
          frame_complete = false;
        }
      }

      seriallogger_string("While count : "+String(mx_res_count));
      mx_res_count++;
    }
    
  FrameType = DISCONNECT_FRAME;
  HdlcWrapperEncoding(FrameType, NULL, 0);
  hdlc_SendPacket(++arrindex, LoadREQframeptr);

  ResByteCount = 0;

  Serial.write(&LoadREQframeptr[arrindex][0], (LoadREQframeptr[arrindex][2] + 2));
  Serial.flush();
  if (METER_DEBUG == TRUE)
  {
    // Serial2.println();
    Serial2.print("TX : ");
    for (int i = 0; i < LoadREQframeptr[arrindex][2] + 2; i++)
    {
      Serial2.print(LoadREQframeptr[arrindex][i], HEX);
      Serial2.print(" ");
    }
      Serial2.println();

  }
  
  
  SerialRead(arrindex, ResByteCount);

  // BREAK METER READING OF NO RESPONSE FROM METER
  if (ResponseBuffer[arrindex][0] != 0x7E || ResponseBuffer[arrindex][2] == 0 /*|| WiFi.softAPgetStationNum() > 0*/)
  {
    seriallogger_string("NO REPONSE/INVALID RESPONSE");
    return 0;
  }

  ObiscodeIndex = 0;
  g_RRR = 0;
  g_SSS = 0;


/////////////////////////////////////////////////////////////////////////////////////////

  appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,"$");
  // appendFile_new(LittleFS,Load_Data_FIle_With_BlockID,"\",\"gwid\":\"" + GWID + "\"}");
  String temp_load_data_string_for_validation = ReadMSNFromFile(Load_Data_FIle_With_BlockID);
  // readFile(LittleFS,Load_Data_FIle_With_BlockID);
   seriallogger_string("billing data " + String(temp_load_data_string_for_validation));
  
  
  if (temp_load_data_string_for_validation.startsWith("$"))
  {
    temp_load_data_string_for_validation.trim();
    if (temp_load_data_string_for_validation.endsWith("$"))
    {
           return 1 ;
    }
    else
    {
      LittleFS.remove(Load_Data_FIle_With_BlockID);
      return 0;
    }
  }
  else
  {
    LittleFS.remove(Load_Data_FIle_With_BlockID);
    return 0;
  }


  return 1 ;
}
