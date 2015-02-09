#include "SerialCommand.h"
#include "SDPMotors.h"
#include <Wire.h>
// test purposes, change to 1 when confident with timings
#define KICK_POWER 1
#define KICK_DURATION 350

#define KICK_TO_GRAB 130

#define KICK_HAPPENING 1
#define KICK_COOLDOWN 2
#define GRAB_HAPPENING 3
MotorBoard motors;
SerialCommand comm;

enum MOTORS {
  LEFT_ENGINE = 4,
  RIGHT_ENGINE = 0,
  KICKER = 3,
  MAX_ENGINES = 6
};

float MAX_SPEED = 1; // TODO: get real value, etc

// 0 -> not kicking, 1 -> kicking, 2 -> getting back to position
byte IS_KICKING = 0;

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
  Serial.println("Team2GO");
  motors.stop_all();
  
  // performs a kick
  comm.addCommand("KICK", kick);
  
  comm.addCommand("GRAB", grab);
  
  
  // sets two speed/accel values for movement engines
  comm.addCommand("MOVE", move_bot);
  
  // sets speed/accel values for a given engine
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
      Serial.println("Retracting kicker");
      IS_KICKING = KICK_COOLDOWN;
      motors.stop_motor(KICKER);  // should be stopped by design, but w/e
      delay(1);  // give it some time to stop properly
      motors.run_motor(KICKER, -1.0, KICK_TO_GRAB, 0);
    }
    break;
  case KICK_COOLDOWN:
    if (!motors.is_running(KICKER)) {
      IS_KICKING = 0;
    }
    break;
  case GRAB_HAPPENING:
    if (!motors.is_running(KICKER)) {
        IS_KICKING = 0;
    }
  default:
    break; // do nothing
  }
  
  // if kicker is running, it will be ignored, all other commands won't be blocked
  comm.readSerial();
  Serial.flush();  // flushing stuff out just in case
  // parsing stuff out every 100ms for debug
  delay(1);
}

void kick_master(int flag, uint16_t duration) {  
  if (IS_KICKING == 0) {
    float power;
    if (!get_float(power))
      power = KICK_POWER;
    // if we use 1/2 power the kick should take 2 times as long, no?
    motors.run_motor(KICKER, power, uint16_t(float(duration) / abs(power)), 0);
    IS_KICKING = flag;
  }
}

/* KICK [POWER(0;1]=1] */
void kick() {
  kick_master(KICK_HAPPENING, KICK_DURATION);
}
void grab() {
  kick_master(GRAB_HAPPENING, KICK_TO_GRAB);
}
/* MOVE LEFT_POWER RIGHT_POWER LEFT_DURATION [RIGHT_DURATION=LEFT_DURATION] */
void move_bot() {
  float left, right;
  uint16_t l_time, r_time;
  if (!get_float(left)) { Serial.println("Can't get left");return;}
  if (!get_float(right)) { Serial.println("Can't get right");return;}
  if (!get_uint16(l_time)) {
    Serial.println("Can't get left time");
    //TODO: signal error?
    return;
  }
  if (!get_uint16(r_time))
    r_time = l_time;
  uint16_t l_lag = 0, r_lag = 0;
  // if it takes more time for left one to activate, then start running right one a bit later
  if (ENGINE_ACTIVATION[LEFT_ENGINE] > ENGINE_ACTIVATION[RIGHT_ENGINE])
    r_lag = ENGINE_ACTIVATION[LEFT_ENGINE] - ENGINE_ACTIVATION[RIGHT_ENGINE];
  else
    l_lag =  ENGINE_ACTIVATION[RIGHT_ENGINE] - ENGINE_ACTIVATION[LEFT_ENGINE];
  motors.run_motor(LEFT_ENGINE, left, l_time, l_lag);
  motors.run_motor(RIGHT_ENGINE, right, r_time, r_lag);
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
  
  motors.run_motor(id, power, time, -1);
  
}

void invalid_command(const char * command) {
  Serial.println(command);
}
