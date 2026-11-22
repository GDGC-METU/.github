#include <Servo.h>

// Calibrate with the horn disconnected and mechanism unloaded.
const byte SERVO_PIN = 9;
const int SAFE_ANGLE = 90;
const int PLASTIC_ANGLE = 35;
const int PAPER_ANGLE = 90;
const int METAL_ANGLE = 145;
const unsigned long COMMAND_TIMEOUT_MS = 10000;

Servo gateServo;
char lineBuffer[32];
byte lineLength = 0;
unsigned long lastCommandMs = 0;

void moveToSafe() { gateServo.write(SAFE_ANGLE); }

void handleLine(const char *line) {
  if (strcmp(line, "SORT:PLASTIC") == 0) {
    gateServo.write(PLASTIC_ANGLE); Serial.println("ACK:PLASTIC");
  } else if (strcmp(line, "SORT:PAPER") == 0) {
    gateServo.write(PAPER_ANGLE); Serial.println("ACK:PAPER");
  } else if (strcmp(line, "SORT:METAL") == 0) {
    gateServo.write(METAL_ANGLE); Serial.println("ACK:METAL");
  } else if (strcmp(line, "SORT:UNKNOWN") == 0) {
    moveToSafe(); Serial.println("ACK:UNKNOWN");
  } else {
    moveToSafe(); Serial.println("ERR:COMMAND");
  }
}

void setup() {
  Serial.begin(9600);
  gateServo.attach(SERVO_PIN);
  moveToSafe();
  lastCommandMs = millis();
  Serial.println("READY");
}

void loop() {
  while (Serial.available() > 0) {
    char incoming = Serial.read();
    if (incoming == '\n') {
      lineBuffer[lineLength] = '\0';
      if (lineLength > 0 && lineBuffer[lineLength - 1] == '\r') lineBuffer[lineLength - 1] = '\0';
      handleLine(lineBuffer);
      lastCommandMs = millis();
      lineLength = 0;
    } else if (lineLength < sizeof(lineBuffer) - 1) {
      lineBuffer[lineLength++] = incoming;
    } else {
      lineLength = 0;
      moveToSafe();
      Serial.println("ERR:TOO_LONG");
    }
  }
  if (millis() - lastCommandMs >= COMMAND_TIMEOUT_MS) moveToSafe();
}
