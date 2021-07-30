//Tablet/Capper/Liquid handling system
//ZBS Scientific, Shanghai, China
//ver 1.6

//Pin definition is from ramps 1.4 using Mega2560
//interupt pins for Mega2560: 2, 3, 18, 19, 20, 21
//Small switch 0(LOW) for switch trigged, normal = 1(HIGH), thee backwire is not used.
//Tablet stepper, microstepping = 2, //8 mm screw
//steps_per_mm = 2x200/8 = 50

#define X_MIN_PIN 3 //homing Z1
#define X_MAX_PIN 2

#define Y_MIN_PIN 14 //homing Z2
#define Y_MAX_PIN 15 //Tablet sensing

#define Z_MIN_PIN 18 //homing Z3
#define Z_MAX_PIN 19

// Pins for Steppers
//
#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38
#define X_CS_PIN 53

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56
#define Y_CS_PIN 49

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62
#define Z_CS_PIN 40

#define E0_STEP_PIN 26
#define E0_DIR_PIN 28
#define E0_ENABLE_PIN 24
#define E0_CS_PIN 42

#define E1_STEP_PIN 36
#define E1_DIR_PIN 34
#define E1_ENABLE_PIN 30
#define E1_CS_PIN 44


// MOSFETs, 4 available
//
#define RAMPS_D7_PIN 7 //HE1
#define RAMPS_D8_PIN 8 //hot bed, big 
#define RAMPS_D9_PIN 9 //fan
#define RAMPS_D10_PIN 10 //heater 0 


#include <AccelStepper.h>

AccelStepper stepper_Z3(1, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepper_Z2(1, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepper_Z1(1, Z_STEP_PIN, Z_DIR_PIN);
//AccelStepper stepper_Z4(1, E0_STEP_PIN, E0_DIR_PIN);

void setup()
{
  Serial.begin(115200);
  while (!Serial); // Wait for port to be ready
  while (Serial.read() >= 0) {} //clear input buffer
  Serial.println(F("++++++++++++++++++++++++++++++++++++++"));
  Serial.println(F("+Tablet/Capper/Liquid handling system+"));
  Serial.println(F("+ ZBS Scientific, Shanghai, China ++++"));
  Serial.println(F("++    Copyright 2021    ++++++++++++++"));
  Serial.println(F("++++++++++++++++++++++++++++++++++++++"));
  Serial.println(F("v1.8"));
  Serial.println(F("Ready to revceive command:"));

  pinMode(X_MIN_PIN, INPUT_PULLUP);
  pinMode(X_MAX_PIN, INPUT_PULLUP);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);
  pinMode(Y_MAX_PIN, INPUT_PULLUP);
  pinMode(Z_MAX_PIN, INPUT_PULLUP);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);

  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);

  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);

  pinMode(Z_ENABLE_PIN, OUTPUT);
  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);

  pinMode(E0_ENABLE_PIN, OUTPUT);
  pinMode(E0_STEP_PIN, OUTPUT);
  pinMode(E0_DIR_PIN, OUTPUT);

  pinMode(E1_ENABLE_PIN, OUTPUT);
  pinMode(E1_STEP_PIN, OUTPUT);
  pinMode(E1_DIR_PIN, OUTPUT);

  digitalWrite(X_DIR_PIN, LOW);
  digitalWrite(X_ENABLE_PIN, LOW); // Enable driver
  digitalWrite(Y_DIR_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW); // Enable driver
  digitalWrite(Z_DIR_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW); // Enable driver
//  digitalWrite(E0_DIR_PIN, LOW);
//  digitalWrite(E0_ENABLE_PIN, LOW); // Enable driver

  stepper_Z1.setMaxSpeed(3000);
  stepper_Z1.setAcceleration(3000);

  stepper_Z2.setMaxSpeed(3000);
  stepper_Z2.setAcceleration(3000);

  stepper_Z3.setMaxSpeed(3000);
  stepper_Z3.setAcceleration(3000);

  digitalWrite(E1_DIR_PIN, LOW); // May set the direction of DC-motor
  digitalWrite(E1_ENABLE_PIN, HIGH); // disable E1 stepper
}


void MOSFET_on(int index)
{
  digitalWrite(index, HIGH);
}

void MOSFET_off(int index)
{
  digitalWrite(index, LOW);
}

//The stepper E1 driver was used to control a DC motor
void dc_motor(int rotate_time, int rotate_speed)
{
  digitalWrite(E1_ENABLE_PIN, LOW); //enable motor
  //generate two pusles
  digitalWrite(E1_STEP_PIN, LOW);
  delay(5);
  digitalWrite(E1_STEP_PIN, HIGH);
  delay(5);
  digitalWrite(E1_STEP_PIN, LOW);
  delay(5);
  digitalWrite(E1_STEP_PIN, HIGH);
  delay(5);
  analogWrite(E1_ENABLE_PIN, rotate_speed);
  delay(rotate_time);
  digitalWrite(E1_ENABLE_PIN, HIGH); //disable motor
}

//Use the DC motor to eject tablet
void eject()
{
  dc_motor(1500, 120);
  delay(100);
  dc_motor(1500, 120);
}

int MAX_STEPS = 30000; //stop homing after MAX_STEPS
void home_Z1()
{
  long initial_homing = -1; // Used to Home Stepper at startup
  while (digitalRead(Z_MIN_PIN) == HIGH && initial_homing >= -1 * MAX_STEPS)
  { // Make the Stepper move until the switch is activated
    stepper_Z1.moveTo(initial_homing); // Set the position to move to
    initial_homing--;                  // Decrease by 1 for next move if needed
    stepper_Z1.run();                  // Start moving the stepper
  }
  stepper_Z1.setCurrentPosition(0);    // Set the current position as zero for now
  initial_homing = 1;
  while (digitalRead(Z_MIN_PIN) == LOW)
  { // Make the Stepper move until the switch is deactivated
    stepper_Z1.moveTo(initial_homing);
    initial_homing++;
    stepper_Z1.run();
  }
  stepper_Z1.setCurrentPosition(0);
}


void home_Z2()
{
  long initial_homing = -1; // Used to Home Stepper at startup

  while (digitalRead(Y_MIN_PIN) == HIGH && initial_homing >= -1 * MAX_STEPS)
  { // Make the Stepper move until the switch is activated
    stepper_Z2.moveTo(initial_homing); // Set the position to move to
    initial_homing--;                  // Decrease by 1 for next move if needed
    stepper_Z2.run();                  // Start moving the stepper
  }
  stepper_Z2.setCurrentPosition(0);    // Set the current position as zero for now
  initial_homing = 1;
  while (digitalRead(Y_MIN_PIN) == LOW)
  { // Make the Stepper move until the switch is deactivated
    stepper_Z2.moveTo(initial_homing);
    initial_homing++;
    stepper_Z2.run();
  }
  stepper_Z2.setCurrentPosition(0);
}


void home_Z3()
{
  long initial_homing = -1;
  while (digitalRead(X_MIN_PIN) == HIGH && initial_homing >= -1 * MAX_STEPS)
  { // Make the Stepper move until the switch is activated
    stepper_Z3.moveTo(initial_homing); // Set the position to move to
    initial_homing--;                  // Decrease by 1 for next move if needed
    stepper_Z3.run();                  // Start moving the stepper
  }
  stepper_Z3.setCurrentPosition(0);    // Set the current position as zero for now
  initial_homing = 1;
  while (digitalRead(X_MIN_PIN) == LOW)
  { // Make the Stepper move unti9ijn  l the switch is deactivated
    stepper_Z3.moveTo(initial_homing);
    initial_homing++;
    stepper_Z3.run();
  }
  stepper_Z3.setCurrentPosition(0);
}


// Communication protocol: e.g.; home_Z1$0
String cmd; //指令
int data; //参数
char delimiter = '$'; //seperator between cmd and data
char terminator = '\n';
String ending;

void loop()
{
  if (Serial.available())
  { // 检查串口缓存是否有数据等待传输
    cmd = Serial.readStringUntil(delimiter); // 获取电机指令中指令信息
    data = Serial.parseInt(); // 获取电机指令中参数信息
    ending = Serial.readStringUntil(terminator);
    Serial.println(F("ok"));
    Serial.print(F("cmd = "));
    Serial.print(cmd);
    Serial.print(F(", "));
    Serial.print(F("data = "));
    Serial.println(data);        
    runUsrCmd();
  }
}

// Communication protocol: e.g.; return:  '1000, finish'
void runUsrCmd()
{

  if (cmd == "home_Z1")  //e.g., commond = 'home_Z1$0'
  {
    home_Z1();
    Serial.println("finish");
    return;
  }

  if (cmd == "home_Z2")
  {
    home_Z2();
    Serial.println("finish");
    return;
  }

  if (cmd == "home_Z3")
  {
    home_Z3();
    Serial.println("finish");
    return;
  }

  if (cmd == "position_Z1")
  {
    Serial.print(stepper_Z1.currentPosition());
    Serial.println(", finish");
    return;
  }

  if (cmd == "position_Z2")
  {
    Serial.print(stepper_Z2.currentPosition());
    Serial.println(", finish");
    return;
  }

  if (cmd == "position_Z3")
  {
    Serial.print(stepper_Z3.currentPosition());
    Serial.println(", finish");
    return;
  }

  if (cmd == "move_Z1")
  {
    stepper_Z1.runToNewPosition(stepper_Z1.currentPosition() + data);
    Serial.println("finish");
    return;
  }

  if (cmd == "move_Z2")
  {
    stepper_Z2.runToNewPosition(stepper_Z2.currentPosition() + data);
    Serial.println("finish");
    return;
  }

  if (cmd == "move_Z3")
  {
    stepper_Z3.runToNewPosition(stepper_Z3.currentPosition() + data);
    Serial.println("finish");
    return;
  }

  
  if (cmd == "set_max_speed_Z1")
  {
    stepper_Z1.setMaxSpeed(data);
    Serial.println("finish");
    return;
  }

  if (cmd == "set_max_speed_Z2")
  {
    stepper_Z2.setMaxSpeed(data);
    Serial.println("finish");
    return;
  }

  if (cmd == "set_max_speed_Z3")
  {
    stepper_Z3.setMaxSpeed(data);
    Serial.println("finish");
    return;
  }


  if (cmd == "move_to_Z1")
  {
    stepper_Z1.runToNewPosition(data);
    Serial.println("finish");
    return;
  }

  if (cmd == "move_to_Z2")
  {
    stepper_Z2.runToNewPosition(data);
    Serial.println("finish");
    return;
  }

  if (cmd == "move_to_Z3")
  {
    stepper_Z3.runToNewPosition(data);
    Serial.println("finish");
    return;
  }

  //tablet functions
  if (cmd == "pickup_tablet") //Z2 was used for cap handling
  {
    stepper_Z2.move(data);
    //Serial.println(stepper_tablet.distanceToGo());
    while (stepper_Z2.distanceToGo() > 0)
    {
      if (digitalRead(Y_MAX_PIN) == LOW)
      {
        Serial.print("success,");
        stepper_Z2.stop();
        break;
      }
      stepper_Z2.run();
    }
    Serial.println("finish");
    stepper_Z2.setCurrentPosition(stepper_Z2.currentPosition());
    return;
  }

  if (cmd == "drop_tablet")
  {
    //    if (digitalRead(Z_MAX_PIN) == HIGH)
    //    {
    //      Serial.println("error, no tablet attached.");
    //      return;
    //    }
    eject();
    Serial.println("finish");
    return;
  }

  if (cmd == "version")
  {
    Serial.println("ZBS Z_platform v 1.6 finish");
    return;
  }

  Serial.println(F("unknown command"));
}
