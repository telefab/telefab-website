/*
 Switch to tell if the FabLab is open or closed
 */

#include <SPI.h>
#include <Ethernet.h>

// Pins
const int buttonPin = 2;
const int redLedPins[] = {A3, A4, A5};
const int greenLedPins[] = {A0, A1, A2};
const int ledPins = 3;

// Working delays (ms)
const unsigned int buttonCheckDelay = 100;
const unsigned int webCheckDelay = 1 * 60 * 1000;
const unsigned int maxClientWaitDelay = 45 * 1000;

// Network configuration (SET THE RIGHT PASSWORD IN THE URL)
byte mac[] = { 
  0x90, 0xA2, 0xDA, 0x0D, 0x6E, 0x25 };
char serverName[] = "telefab.fr";
char apiURL[] = "/lab/api/lieu?password=toto";

// Current status
int isOpen = -1; // -1 = unknown
int buttonPushed = 0;
int blinkVar = 0;
unsigned int lastButtonCheck = 0;
unsigned int lastWebCheck = 0;
int checkButtonNow = 0;
int checkWebNow = 0;

// Connection variables
EthernetClient checkClient;
EthernetClient sendClient;
String receivedCheck = "";
String receivedSend = "";
unsigned int lastCheckClient = 0;
unsigned int lastSendClient = 0;

void setup() {
  // pin modes
  for (int i = 0; i < ledPins; i++) {
    pinMode(redLedPins[i], OUTPUT);      
    pinMode(greenLedPins[i], OUTPUT); 
  }
  // Debug output
  Serial.begin(9600);
  // Initialize the connection
  initializeNetwork();
}

void loop() {
  // What should be done this loop?
  unsigned int now = millis();
  checkButtonNow = (lastButtonCheck == 0 || lastButtonCheck > now || (now - lastButtonCheck >= buttonCheckDelay));
  checkWebNow = (lastWebCheck == 0 || lastWebCheck > now || (now - lastWebCheck >= webCheckDelay));
  if (checkButtonNow)
    lastButtonCheck = now;
  if (checkWebNow)
    lastWebCheck = now;
  
  // Read the button value and control the LEDs
  if (checkButtonNow) {
    readButton();
    controlLEDs();
  }
    
  // Check status on the web (even if not to check because receiving data takes time)
  checkWeb(0);
  
  // Read send to web result if any
  readSendWeb();
}

void initializeNetwork() {
  // attempt a DHCP connection:
  Serial.println("Attempting to get an IP address using DHCP:");
  while (!Ethernet.begin(mac)) {
    // if DHCP fails, try again
    Serial.println("failed to get an IP address using DHCP, trying again");
  }
  Serial.print("My address: ");
  Serial.println(Ethernet.localIP());
}

void readButton() {
  // Read the button
  int buttonValue = digitalRead(buttonPin);
  
  // Detect if button has just been pushed
  if (buttonValue && !buttonPushed && isOpen != -1) {
    int nextOpen = !isOpen;
    isOpen = -1;
    sendWeb(nextOpen);
  }
  buttonPushed = buttonValue;
}

void controlLEDs() {
  // Switch the proper LED on, or blink if unknown
  if (isOpen == 0 || isOpen == 1) {
      // Stable state
      int greenState = LOW;
      int redState = LOW;
      if (isOpen == 1) {
        // Open
        greenState = HIGH;
      } else if (isOpen == 0) {
        // Closed
        redState = HIGH; 
      }
      for (int i = 0; i < ledPins; i++) {
        digitalWrite(greenLedPins[i], greenState);
        digitalWrite(redLedPins[i], redState);
      }
  } else {
      // Blinking state
      static int blinkState = 0;
      for (int i = 0; i < ledPins; i++) {
        digitalWrite(greenLedPins[i], i == (blinkState/2 % 3));
        digitalWrite(redLedPins[i], i == (blinkState/2 % 3));
      }
      blinkState++;
      if (blinkState >= 6)
          blinkState = 0;
  }
}

void checkWeb(int force) {
  // Read the current status on the Web
  if (checkClient.connected()) {
    unsigned int now = millis();
    if (lastCheckClient > now || (now - lastCheckClient >= maxClientWaitDelay)) {
      // Stop the connection on timeout
      checkClient.stop();
    } else if (checkClient.available()) {
      // Receiving data
      char inChar = checkClient.read();
      if (inChar == '\n')
        receivedCheck = "";
      else
        receivedCheck+= inChar;
      if (receivedCheck == "OPEN" || receivedCheck == "CLOSED") {
        Serial.print("Received web status: ");
        Serial.println(receivedCheck);
        isOpen = receivedCheck == "OPEN";
        checkClient.stop();
      }
    }
  } else if (checkWebNow || force) {
    // Starting a request
    Serial.println("Starting a web request to get current status");
    isOpen = - 1;
    if (checkClient.connect(serverName, 80)) {
      String toSend = "GET ";
      toSend+= apiURL;
      toSend+= " HTTP/1.1";
      checkClient.println(toSend);
      toSend = "HOST: ";
      toSend+= serverName;
      checkClient.println(toSend);
      checkClient.println();
      lastCheckClient = millis();
    }
  }
}

void sendWeb(int setOpen) {
    // Send the new status to the API
    Serial.print("Starting a web request to set current status to ");
    Serial.println(setOpen);
    if (sendClient.connect(serverName, 80)) {
      String toSend = "POST ";
      toSend+= apiURL;
      toSend+= " HTTP/1.1";
      sendClient.println(toSend);
      toSend = "HOST: ";
      toSend+= serverName;
      sendClient.println(toSend);
      sendClient.println("Content-Type: application/x-www-form-urlencoded");
      sendClient.println("Content-Length: 6");
      sendClient.println();
      sendClient.print("open=");
      sendClient.println(setOpen);
      sendClient.println();
      lastSendClient = millis();
    }
}

void readSendWeb() { 
  // Read the result of a send to web 
  if (sendClient.connected()) {
    unsigned int now = millis();
    if (lastSendClient > now || (now - lastSendClient >= maxClientWaitDelay)) {
      // Stop the connection on timeout
      sendClient.stop();
    } else if (sendClient.available()) {
      // Receiving data
      char inChar = sendClient.read();
      if (inChar == '\n')
        receivedSend = "";
      else
        receivedSend+= inChar;
      if (receivedSend == "OK" || receivedSend == "ERROR") {
        Serial.print("Set status result: ");
        Serial.println(receivedSend);
        sendClient.stop();
        // Force to check the new status
        checkWeb(1);
      }
    }
  }
}
