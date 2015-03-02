#include "SerialCommand.h"
#include "SDPMotors.h"
#include <Wire.h>
// test purposes, change to 1 when confident with timings
#define KICK_POWER -1
#define GRAB_POWER 1
#define KICK_DURATION 250
#define GRAB_DURATION 220

#define ACK_COMMS
// intermediate state
#define HAPPENING 1
// finished state
#define COMPLETE 2
// negative intermediate state
#define CLOSING 3

MotorBoard motors;
SerialCommand comm;

enum MOTORS {
  LEFT_ENGINE = 4,
  RIGHT_ENGINE = 0,
  KICKER = 3,
  GRABBER = 2,
  MAX_ENGINES = 6
};

// 0 -> not kicking, 1 -> kicking, 2 -> getting back to position
byte IS_KICKING = 0;
// 0 -> closed, 1 -> opening, 2 -> opened, 3 -> closing
byte IS_GRABBER_OPEN = 0;
byte MATCHED=0;
byte KICK_AFTERWARDS = 0;

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

long t;
void setup() {
  Serial.begin(115200);  // 115kb
  setup_pins();
  Wire.begin();  // need this s.t. arduino is mastah
  Serial.println("Team2GO");
  Serial.flush();
  motors.stop_all();
  
  // performs a kick
  comm.addCommand("KICK", kick);
  
  comm.addCommand("GRAB", grab);
    
  // sets two speed/accel values for movement engines
  comm.addCommand("MOVE", move_bot);
  
  // sets speed/accel values for a given engine
  comm.addCommand("RUN_ENGINE", run_engine);
  comm.addCommand("STOP", stop_engines);
  comm.setDefaultHandler(invalid_command);
  read_all();
  t = millis();
}

void read_all() {
  for (int i = 0; i < 128 && Serial.available(); i++)
    Serial.read();
}

void kick_f(float power) {
  motors.run_motor(KICKER, power, uint16_t(float(KICK_DURATION) / abs(power)), 0);
}
void loop() {
  // check whether something needs to be stopped
  motors.scan_motors();
  
  // if kicking -> check whether we need to start retracting the kicker, etc
  switch(IS_KICKING) {
  case HAPPENING:
    if (!motors.is_running(KICKER)) {
      IS_KICKING = 0;
      break;
      IS_KICKING = COMPLETE;
      motors.stop_motor(KICKER);  // should be stopped already, but w/e
      delay(3);  // give it some time to stop properly
      motors.run_motor(KICKER, -1, KICK_DURATION*7/10, 0);
    }
    break;
  case COMPLETE:
    if (!motors.is_running(KICKER)) {
      IS_KICKING = 0;
    }
    break;
  default:
    break; // do nothing
  }
  switch(IS_GRABBER_OPEN) {
  case HAPPENING:
    if (!motors.is_running(GRABBER)) {
      IS_GRABBER_OPEN = COMPLETE;
      motors.stop_motor(GRABBER);
      if (KICK_AFTERWARDS == 1) {
          kick_f(KICK_POWER);
          KICK_AFTERWARDS = 0;
      }
      delay(3);
    }
    break;
  case CLOSING:
    if (!motors.is_running(GRABBER)) {
      IS_GRABBER_OPEN = 0;
      motors.stop_motor(GRABBER);
    }
    break;
  default:
    break;
  }
  comm.readSerial();
  if (MATCHED == 1) {
    read_all();
  }
  MATCHED=0;
  Serial.flush();
    // flushing stuff out just in case
  // parsing stuff out every 100ms for debug
  delay(5);
}

void stop_engines() {
  MATCHED=1;
  // only stops movement engines!
  motors.stop_motor(LEFT_ENGINE);
  motors.stop_motor(RIGHT_ENGINE);
}
/* KICK [POWER(0;1]=1] */
void kick() {
  MATCHED=1;
#ifdef ACK_COMMS  
  Serial.println("ACKKICKACKKICKACKKICK");
#endif
  if (IS_GRABBER_OPEN == COMPLETE) {
    
    float power;
    if (!get_float(power))
      power = KICK_POWER;
    
  }
  else {
    grab();
    KICK_AFTERWARDS = 1;
  }
}
void grab() {
  MATCHED = 1;
#ifdef ACK_COMMS
  Serial.println("ACKGRABACKGRABACKGRAB");
#endif
  float power;
  if (!get_float(power))
    power = GRAB_POWER;
  if (IS_GRABBER_OPEN == COMPLETE) {
    power = -power;
  }
  if (IS_GRABBER_OPEN == HAPPENING || IS_GRABBER_OPEN == CLOSING)
    return;
  if (IS_GRABBER_OPEN == 0)
    IS_GRABBER_OPEN = HAPPENING;
  else
    IS_GRABBER_OPEN = CLOSING;
  motors.run_motor(GRABBER, power, uint16_t(float(GRAB_DURATION) / abs(power)), 0);
}
/* MOVE LEFT_POWER RIGHT_POWER LEFT_DURATION [RIGHT_DURATION=LEFT_DURATION] */
void move_bot() {
  MATCHED=1;
  float left, right;
  uint16_t l_time, r_time;
#ifdef ACK_COMMS
  Serial.println("ACKMOVEACKMOVEACKMOVE");
#endif
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
  MATCHED=1;
  float power;
  uint16_t id, time;
#ifdef ACK_COMMS
  Serial.println("ACKRUN_ENGINEACKRUN_ENGINEACK_RUNENGINE");
#endif
  if (!get_uint16(id)) {Serial.println("failed to get id"); return;}
  if (!get_float(power)) {Serial.println("failed to get power");return;}
  if (!get_uint16(time)) {
    Serial.println("failed to get time");
    return;
  }
  motors.run_motor(id, power, time, -1);
}

void invalid_command(const char * command) {
  MATCHED=0;
  Serial.print("FAIL: ");
  Serial.println(command);
}
