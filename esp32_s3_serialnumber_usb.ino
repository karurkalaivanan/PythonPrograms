#include <HardwareSerial.h>

// RS485 configuration
#define RS485_BAUD 9600
#define DEBUG_BAUD 115200

// RS485 Driver control pin (DE/RE)
#define RS485_TxRx 41

// Relay control pins
#define RELAY1 21
#define RELAY2 47
#define RELAY3 48
#define RELAY4 42

// UART2 pins for fallback debugging
#define DEBUG_TX 17
#define DEBUG_RX 18

// DLMS Commands
const uint8_t snrmRequest[] = {0x7E, 0xA0, 0x07, 0x03, 0x21, 0x93, 0x0F, 0x01, 0x7E};
const uint8_t aarqRequest[] = {
  0x7E, 0xA0, 0x2B, 0x03, 0x21, 0x10, 0xFB, 0xAF, 0xE6, 0xE6, 0x00, 0x60, 0x1D,
  0xA1, 0x09, 0x06, 0x07, 0x60, 0x85, 0x74, 0x05, 0x08, 0x01, 0x01, 0xBE, 0x10,
  0x04, 0x0E, 0x01, 0x00, 0x00, 0x00, 0x06, 0x5F, 0x1F, 0x04, 0x00, 0x00, 0x1E,
  0x5D, 0xFF, 0xFF, 0xB3, 0xE2, 0x7E
};
const uint8_t nextCommand[] = {
  0x7E, 0xA0, 0x19, 0x03, 0x21, 0x32, 0x6F, 0xD8, 0xE6, 0xE6, 0x00, 0xC0, 0x01,
  0xC1, 0x00, 0x01, 0x00, 0x00, 0x60, 0x01, 0x00, 0xFF, 0x02, 0x00, 0x89, 0xA0, 0x7E
};
const uint8_t disconnectCommand[] = {0x7E, 0xA0, 0x07, 0x03, 0x21, 0x53, 0x03, 0xC7, 0x7E};

// UART2 for fallback debug
HardwareSerial Debug(2);

// UART0 for RS485 (meter communication)
HardwareSerial SerialMeter(0);

String parseMeterSerial(byte* response, int length) {
  String responseHex = "";
  for (int i = 0; i < length; i++) {
    if (response[i] < 0x10) responseHex += "0";
    responseHex += String(response[i], HEX) + " ";
  }
  Serial.println("Full Response (Hex): " + responseHex); // Use Serial for USB CDC
  Debug.println("Full Response (Hex): " + responseHex);  // Fallback to Debug

  // Validate start and end flags
  if (response[0] != 0x7E || response[length - 1] != 0x7E) {
    Serial.println("Invalid HDLC frame: Missing start or end flag."); // USB
    Debug.println("Invalid HDLC frame: Missing start or end flag.");  // Fallback
    return "";
  }

  // Remove start and end flags
  byte payload[length - 2];
  memcpy(payload, &response[1], length - 2);
  
  Serial.print("Payload (Hex): "); // USB
  Debug.print("Payload (Hex): ");  // Fallback
  for (int i = 0; i < length - 2; i++) {
    if (payload[i] < 0x10) {
      Serial.print("0");
      Debug.print("0");
    }
    Serial.print(payload[i], HEX);
    Debug.print(payload[i], HEX);
    Serial.print(" ");
    Debug.print(" ");
  }
  Serial.println(); // USB
  Debug.println();  // Fallback

  // Adjust offset and length based on debug output
  int startOffset = 16; // Corrected to start at 51 (Q) based on previous analysis
  int serialLength = 8;  // Corrected to length of Q0246117
  if (length - 2 < startOffset + serialLength) {
    Serial.println("Payload too short for serial number extraction."); // USB
    Debug.println("Payload too short for serial number extraction.");  // Fallback
    return "";
  }

  // Explicitly clear the serialNumber buffer
  char serialNumber[serialLength + 1];
  memset(serialNumber, 0, serialLength + 1); // Ensure the entire buffer is zeroed
  memcpy(serialNumber, &payload[startOffset], serialLength);

  // Debug the raw buffer contents
  Serial.print("Raw Serial Number Buffer: "); // USB
  Debug.print("Raw Serial Number Buffer: ");  // Fallback
  for (int i = 0; i < serialLength + 1; i++) {
    if (serialNumber[i] == 0) {
      Serial.print("[NULL]");
      Debug.print("[NULL]");
    } else if (isPrintable(serialNumber[i])) {
      Serial.print(serialNumber[i]);
      Debug.print(serialNumber[i]);
    } else {
      Serial.print("?");
      Debug.print("?");
    }
  }
  Serial.println(); // USB
  Debug.println();  // Fallback

  // Convert to string and return
  String result = String(serialNumber);
  Serial.println("Extracted Serial Number: " + result); // USB
  Debug.println("Extracted Serial Number: " + result);  // Fallback
  return result;
}

void sendCommand(const uint8_t* cmd, size_t len) {
  // Debug print of sent command
  Serial.print("Sending Command (Hex): "); // USB
  Debug.print("Sending Command (Hex): ");  // Fallback
  for (int i = 0; i < len; i++) {
    if (cmd[i] < 0x10) {
      Serial.print("0");
      Debug.print("0");
    }
    Serial.print(cmd[i], HEX);
    Debug.print(cmd[i], HEX);
    Serial.print(" ");
    Debug.print(" ");
  }
  Serial.println(); // USB
  Debug.println();  // Fallback

  digitalWrite(RS485_TxRx, HIGH);   // Enable transmitter
  delayMicroseconds(20);            // Small gap before sending
  SerialMeter.write(cmd, len);
  SerialMeter.flush();              // Wait until all data sent
  delayMicroseconds(20);            // Small gap after sending
  digitalWrite(RS485_TxRx, LOW);    // Back to receive mode
}

void setup() {
  // Start UART2 for fallback debug
  Debug.begin(DEBUG_BAUD, SERIAL_8N1, DEBUG_RX, DEBUG_TX);
  Debug.println("\nStarting ESP32-S3 RS485 Test... (Fallback via UART2)");

  // Initialize USB CDC serial for primary debug output
  Serial.begin(115200); // USB CDC interface
  while (!Serial) {     // Wait for USB CDC to connect
    delay(100);         // Prevent tight looping
    Debug.print(".");   // Indicate waiting on UART2
  }
  Serial.println("\n=== ESP32-S3 USB CDC Debug Started ==="); // USB
  Debug.println("\n=== ESP32-S3 USB CDC Debug Started ===");  // Fallback

  // Start UART0 for RS485
  SerialMeter.begin(RS485_BAUD, SERIAL_8N1, 44, 43); // RX0=GPIO44, TX0=GPIO43
  Serial.println("Debug: UART0 (RS485) initialized"); // USB
  Debug.println("Debug: UART0 (RS485) initialized");  // Fallback

  // RS485 DE/RE pin
  pinMode(RS485_TxRx, OUTPUT);
  digitalWrite(RS485_TxRx, LOW);   // Start in receive mode

  // Relay control pins
  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);
  pinMode(RELAY4, OUTPUT);

  digitalWrite(RELAY1, LOW);
  digitalWrite(RELAY2, HIGH);
  digitalWrite(RELAY3, LOW);
  digitalWrite(RELAY4, LOW);
  Serial.println("Debug: Relay3 enabled"); // USB
  Debug.println("Debug: Relay3 enabled");  // Fallback

  delay(2000); // Allow system to stabilize

  // Send SNRM Request
  Serial.println("Debug: Sending SNRM Request..."); // USB
  Debug.println("Debug: Sending SNRM Request...");  // Fallback
  sendCommand(snrmRequest, sizeof(snrmRequest));
  Serial.println("Debug: Command sent, waiting for response..."); // USB
  Debug.println("Debug: Command sent, waiting for response...");  // Fallback

  // Read initial response
  delay(1000);
  byte response[100];
  int responseLength = SerialMeter.readBytes(response, sizeof(response));
  if (responseLength > 0) {
    String responseHex = "";
    for (int i = 0; i < responseLength; i++) {
      if (response[i] < 0x10) responseHex += "0";
      responseHex += String(response[i], HEX) + " ";
    }
    Serial.println("Debug: Received Response: " + responseHex); // USB
    Debug.println("Debug: Received Response: " + responseHex);  // Fallback

    if (memchr(response, 0x00, responseLength) != NULL) {
      Serial.println("Debug: Null character found. Sending AARQ Request..."); // USB
      Debug.println("Debug: Null character found. Sending AARQ Request...");  // Fallback
      sendCommand(aarqRequest, sizeof(aarqRequest));
      delay(1000);
      byte aarqResponse[200];
      int aarqLength = SerialMeter.readBytes(aarqResponse, sizeof(aarqResponse));
      if (aarqLength > 0) {
        String aarqHex = "";
        for (int i = 0; i < aarqLength; i++) {
          if (aarqResponse[i] < 0x10) aarqHex += "0";
          aarqHex += String(aarqResponse[i], HEX) + " ";
        }
        Serial.println("Debug: Received AARQ Response: " + aarqHex); // USB
        Debug.println("Debug: Received AARQ Response: " + aarqHex);  // Fallback

        if (memchr(aarqResponse, 0x60, aarqLength) != NULL) {
          Serial.println("Debug: AARE success. Sending Next Command..."); // USB
          Debug.println("Debug: AARE success. Sending Next Command...");  // Fallback
          sendCommand(nextCommand, sizeof(nextCommand));
          delay(1000);
          byte nextResponse[200];
          int nextLength = SerialMeter.readBytes(nextResponse, sizeof(nextResponse));
          if (nextLength > 0) {
            String nextHex = "";
            for (int i = 0; i < nextLength; i++) {
              if (nextResponse[i] < 0x10) nextHex += "0";
              nextHex += String(nextResponse[i], HEX) + " ";
            }
            Serial.println("Debug: Received Next Response: " + nextHex); // USB
            Debug.println("Debug: Received Next Response: " + nextHex);  // Fallback
            String serialNumber = parseMeterSerial(nextResponse, nextLength);
            Serial.println("Debug: Meter Serial Number: " + serialNumber); // USB
            Debug.println("Debug: Meter Serial Number: " + serialNumber);  // Fallback
          }
        }
      }
      Serial.println("Debug: Sending Disconnect Command..."); // USB
      Debug.println("Debug: Sending Disconnect Command...");  // Fallback
      sendCommand(disconnectCommand, sizeof(disconnectCommand));
      delay(1000);
      byte disconnectResponse[100];
      int disconnectLength = SerialMeter.readBytes(disconnectResponse, sizeof(disconnectResponse));
      if (disconnectLength > 0) {
        String disconnectHex = "";
        for (int i = 0; i < disconnectLength; i++) {
          if (disconnectResponse[i] < 0x10) disconnectHex += "0";
          disconnectHex += String(disconnectResponse[i], HEX) + " ";
        }
        Serial.println("Debug: Received Disconnect Response: " + disconnectHex); // USB
        Debug.println("Debug: Received Disconnect Response: " + disconnectHex);  // Fallback
      }
    }
  }
}

void loop() {
  // Continuous reading of RS485 responses
  while (SerialMeter.available()) {
    int b = SerialMeter.read();
    Serial.print("Debug: Received: 0x"); // USB
    Debug.print("Debug: Received: 0x");  // Fallback
    if (b < 0x10) {
      Serial.print("0");
      Debug.print("0");
    }
    Serial.println(b, HEX); // USB
    Debug.println(b, HEX);  // Fallback
  }
}
