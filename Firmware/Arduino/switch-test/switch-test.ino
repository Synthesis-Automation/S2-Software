// From ramps
// Limit Switches
//interupt pins for Mega2560 2, 3, 18, 19, 20, 21

#define X_MIN_PIN 3
#define X_MAX_PIN 2 

#define Y_MIN_PIN 14
#define Y_MAX_PIN 15

#define Z_MIN_PIN 18
#define Z_MAX_PIN 19

//
// Steppers
//
#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#ifndef X_CS_PIN
#define X_CS_PIN 53
#endif

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#ifndef Y_CS_PIN
#define Y_CS_PIN 49
#endif

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#ifndef Z_CS_PIN
#define Z_CS_PIN 40
#endif

#define E0_STEP_PIN 26
#define E0_DIR_PIN 28
#define E0_ENABLE_PIN 24
#ifndef E0_CS_PIN
#define E0_CS_PIN 42
#endif

#define E1_STEP_PIN 36
#define E1_DIR_PIN 34
#define E1_ENABLE_PIN 30
#ifndef E1_CS_PIN
#define E1_CS_PIN 44
#endif

//
// Heaters / Fans
// only 4 available

#ifndef RAMPS_D8_PIN
#define RAMPS_D8_PIN 8 //bed, big
#endif
#ifndef RAMPS_D9_PIN
#define RAMPS_D9_PIN 9 //fan
#endif
#ifndef RAMPS_D10_PIN
#define RAMPS_D10_PIN 10 //heater 0 (small, used by us, small))
#endif

#include <AccelStepper.h>
//AccelStepper stepper_X(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepper_up_down(1, Y_STEP_PIN, Y_DIR_PIN); //move up and down
AccelStepper stepper_rotate(1, Z_STEP_PIN, Z_DIR_PIN); //rotate for decap

void setup()
{
  Serial.begin(115200); // Init used serial port
  while (!Serial);   // Wait for port to be ready
  while (Serial.read() >= 0) {} //clear input buffer

  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(X_MAX_PIN, INPUT_PULLUP);

  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MAX_PIN, INPUT_PULLUP); //used for sensing tablet pickup

  pinMode(Z_MIN_PIN, INPUT_PULLUP);
  pinMode(Z_MAX_PIN, INPUT_PULLUP);

  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);

  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);

  digitalWrite(X_DIR_PIN, LOW);
  digitalWrite(X_ENABLE_PIN, LOW); // Enable driver

  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  digitalWrite(Y_DIR_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW); // Enable driver

  pinMode(Z_ENABLE_PIN, OUTPUT);
  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  digitalWrite(Z_DIR_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW); // Enable driver

  Serial.println(F("Ready to revceive command:"));
}


void loop()
{
  int buttonState = digitalRead(Y_MAX_PIN);
  // print out the state of the button:
  // 显示按键状态
  Serial.println(buttonState);
  delay(100);
}
//Connection: input_pullup; among V G S, G and S is used. C is connected to G
//result: NO -> HIGH (normal), LOW(pressed)
//result: NC -> HIGH (pressed), LOW/0 (normal)
