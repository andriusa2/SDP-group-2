#include "SerialCommand.h"
#include "SDPMotors.h"
#include <Wire.h>
// test purposes, change to 1 when confident with timings
#define KICK_POWER 0.5
// 100 ms
#define KICK_DURATION 100

#define KICK_HAPPENING 1
#define KICK_COOLDOWN 2
MotorBoard motors;
SerialCommand comm;

enum MOTORS {
  LEFT_ENGINE = 0,
  RIGHT_ENGINE,
  KICKER,
  MAX_ENGINES
};

float MAX_SPEED = 1; // TODO: get real value, etc

// 0 -> not kicking, 1 -> kicking, 2 -> getting back to position
byte IS_KICKING = 0;
float kick_power;
uint16_t kick_duration;

void setup_pins() {
  pinMode(2,INPUT);
  pinMode(3,OUTPUT);
  pinMode(4,INPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,INPUT);
  pinMode(8,OUTPUT);
  pinMode(9,OUTPUT);
  pinMode(10,INPUT);
  pinMode(11,INPUT);
  pinMode(12,INPUT);
  pinMode(13,OUTPUT); // LED
  pinMode(A0,INPUT);
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  digitalWrite(8,HIGH); //Pin 8 must be high to turn the radio on!
}

/* pushing this as a utility as it's used quite often */
bool get_float(float &first) {
  char *tmp = comm.next();
  if (!tmp) return false;
  first = atof(tmp);
  return true;
}

// actually will never read a full unsigned int, but we don't need it.
bool get_uint16(uint16_t &first) {
  char *tmp = comm.next();
  if (!tmp) return false;
  first = (uint16_t)atoi(tmp);  // should probably check with numerical limits
  return true;
}
/*
command format:
RUN_ENGINE ENGINE_ID POWER[-1;1] DURATION(0;64k]
POWER -> % of engine load, DURATION -> how long should a given engine run in ms (needs to fit into uint16_t)

KICK [POWER(0;1]=1]
Should reset automatically, will block other kicking attempts at the moment

MOVE LEFT_POWER RIGHT_POWER LEFT_DURATION [RIGHT_DURATION=LEFT_DURATION]
*/


void setup() {
  Serial.begin(115200);  // 115kb
  setup_pins();
  Wire.begin();  // need this s.t. arduino is mastah
  
  //motors.diagnostics(1); // small twitches should happen
  motors.stop_all();
  
  // test function
  comm.addCommand("BLINK", my_blink);
  
  // performs a kick
  comm.addCommand("KICK", kick);
  
  // sets two speed/accel values for movement engines
  comm.addCommand("MOVE", move_bot);
  
  // sets speed/accel values for a given engine
  // format A_SET_ENGINE ENG_ID float
  comm.addCommand("RUN_ENGINE", run_engine);
  
  comm.setDefaultHandler(invalid_command);
}

void loop() {
  // check whether something needs to be stopped
  motors.scan_motors();
  
  // if kicking -> check whether we need to start retracting the kicker, etc
  switch(IS_KICKING) {
  case KICK_HAPPENING:
    if (!motors.is_running(KICKER)) {
      motors.run_motor(KICKER, -kick_power, kick_duration);
      IS_KICKING = KICK_COOLDOWN;
    }
    break;
  case KICK_COOLDOWN:
    if (!motors.is_running(KICKER)) {
      IS_KICKING = 0;
    }
    break;
  default:
    break; // do nothing
  }
  
  // if kicker is running, it will be ignored, all other commands won't be blocked
  comm.readSerial();
  
  // parsing stuff out every 100ms for debug
  delay(100);
}

void my_blink() {
  int timeout = 1000;
  for (int i = 0; i < 10; i++) {
    digitalWrite(13, HIGH);
    delay(timeout);
    digitalWrite(13, LOW);
    delay(timeout);
  }
}

/* KICK [POWER(0;1]=1] */
void kick() {
  if (IS_KICKING == 0) {
    float power;
    if (!get_float(power))
      power = KICK_POWER;
    // if we use 1/2 power the kick should take 2 times as long, no?
    kick_power = power;
    kick_duration = KICK_DURATION / power;
    motors.run_motor(KICKER, power, kick_duration);
    IS_KICKING = KICK_HAPPENING;
  }
}

/* MOVE LEFT_POWER RIGHT_POWER LEFT_DURATION [RIGHT_DURATION=LEFT_DURATION] */
void move_bot() {
  float left, right;
  uint16_t l_time, r_time;
  if (!get_float(left) || !get_float(right) || !get_uint16(l_time)) {
    //TODO: signal error?
    return;
  }
  if (!get_uint16(r_time))
    r_time = l_time;
  motors.run_motor(LEFT_ENGINE, left, l_time);
  motors.run_motor(RIGHT_ENGINE, right, r_time);
}

/* RUN_ENGINE ENGINE_ID POWER[-1;1] DURATION(0;64k] */
void run_engine() {
  float power;
  uint16_t id, time;
  if (!get_uint16(id)) {Serial.println("failed to get id"); return;}
  if (!get_float(power)) {Serial.println("failed to get power");return;}
  if (!get_uint16(time)) {
    Serial.println("failed to get time");
    return;
  }
  if (id == KICKER) {
    if (IS_KICKING == 0) {
      motors.run_motor(id, power, time);
      IS_KICKING = KICK_HAPPENING;
      kick_power = power;
      kick_duration = time;
    }
  } else {
    motors.run_motor(id, power, time);
  }
}

void invalid_command(const char * command) {
  Serial.println(command);
}
