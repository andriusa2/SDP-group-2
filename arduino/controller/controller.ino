#include "SerialCommand.h"
#include "SDPMotors.h"
#include <Wire.h>
// test purposes, change to 1 when confident with timings
#define KICK_POWER 1
#define GRAB_POWER -1
#define KICK_DURATION 190
#define GRAB_DURATION 200

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
  LF_MOTOR = 0,
  LB_MOTOR = 4,
  RF_MOTOR = 1,
  RB_MOTOR = 5,
  KICKER = 3,
  GRABBER = 2,
  MAX_ENGINES = 6
};

uint8_t movement_motors[] = {LF_MOTOR, LB_MOTOR, RF_MOTOR, RB_MOTOR};

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

bool get_int16(int16_t &first) {
  char * tmp = comm.next();
  if (!tmp) return false;
  first = (int)atoi(tmp);
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
  Serial.flush();
  motors.stop_all();
  
  // performs a kick
  comm.addCommand("KICK", kick);
  
  comm.addCommand("OPEN", grab);
  comm.addCommand("CLOSE", grab_close);
    
  // sets two speed/accel values for movement engines
  comm.addCommand("MOVE", move_bot);
  
  // sets speed/accel values for a given engine
  comm.addCommand("RUN_ENGINE", run_engine);
  comm.addCommand("STOP", stop_engines);
  comm.setDefaultHandler(invalid_command);
  read_all();
}

void read_all() {
  for (int i = 0; i < 128 && Serial.available(); i++)
    Serial.read();
}

void kick_f(float power) {
  IS_KICKING = HAPPENING;
  motors.run_motor(KICKER, power, uint16_t(float(KICK_DURATION) / abs(power)), 0);
}

void loop() {
  // check whether something needs to be stopped
  motors.scan_motors();
  
  // if kicking -> check whether we need to start retracting the kicker, etc
  switch(IS_KICKING) {
  case HAPPENING:
    if (!motors.is_running(KICKER)) {
      motors.stop_motor(KICKER);  // should be stopped already, but w/e
      delay(3);
      kick_f(-1.0 * KICK_POWER);
      IS_KICKING = COMPLETE;
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
    }
    break;
  case CLOSING:
    if (!motors.is_running(GRABBER)) {
      IS_GRABBER_OPEN = 0;
      motors.stop_motor(GRABBER);
    }
    break;
  case COMPLETE:
    if (KICK_AFTERWARDS == 1) {
      kick_f(KICK_POWER);
      KICK_AFTERWARDS = 0;
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
  delay(5);
}

void stop_engines() {
  MATCHED=1;
  // only stops movement engines!
  
#ifdef ACK_COMMS  
  Serial.println("ACKSTOPACKSTOPACKSTOP");
#endif
  motors.stop_motor(LF_MOTOR);
  motors.stop_motor(LB_MOTOR);
  motors.stop_motor(RF_MOTOR);
  motors.stop_motor(RB_MOTOR);
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
      power = 1;
    kick_f(abs(power) * KICK_POWER);
  }
  else {
    grab();
    KICK_AFTERWARDS = 1;
  }
}

// OPEN GRABBER
void grab() {
  MATCHED = 1;
#ifdef ACK_COMMS
  Serial.println("ACKOPENACKOPENACKOPEN");
#endif
  float power;
  if (!get_float(power))
    power = GRAB_POWER;
  if (IS_GRABBER_OPEN != 0)
    return;
  IS_GRABBER_OPEN = HAPPENING;
  motors.run_motor(GRABBER, abs(power) * GRAB_POWER, uint16_t(float(GRAB_DURATION) / abs(power)), 0);
}
// close grab
void grab_close() {
  MATCHED = 1;
#ifdef ACK_COMMS
  Serial.println("ACKCLOSEACKCLOSEACKCLOSE");
#endif
  float power;
  if (!get_float(power))
    power = GRAB_POWER;
  if (IS_GRABBER_OPEN != COMPLETE)
    return;
  IS_GRABBER_OPEN = CLOSING;
  motors.run_motor(GRABBER, -abs(power) * GRAB_POWER, uint16_t(float(GRAB_DURATION) / abs(power)), 0);
}

/* MOVE LEFT_POWER RIGHT_POWER LEFT_DURATION [RIGHT_DURATION=LEFT_DURATION] */
void move_bot() {
  MATCHED=1;
  int16_t lf, lb, rf, rb;
  uint16_t lag = motors.get_max_lag(movement_motors, 4);
  if (!get_int16(lf)) {
    Serial.println("Can't get left time");
    return;
  }
  if (!get_int16(lb)) {
    Serial.println("Can't get left time");
    return;
  }
  if (!get_int16(rf)) {
    Serial.println("Can't get left time");
    return;
  }
  if (!get_int16(rb)) {
    Serial.println("Can't get left time");
    return;
  }
  
#ifdef ACK_COMMS
  Serial.println("ACKMOVEACKMOVEACKMOVE");
#endif
  
  motors.run_motor(LF_MOTOR, lf > 0? 1 : -1, abs(lf), motors.get_adj_lag(LF_MOTOR, lag));
  motors.run_motor(LB_MOTOR, lb > 0? 1 : -1, abs(lb), motors.get_adj_lag(LB_MOTOR, lag));
  motors.run_motor(RF_MOTOR, rf > 0? 1 : -1, abs(rf), motors.get_adj_lag(RF_MOTOR, lag));
  motors.run_motor(RB_MOTOR, rb > 0? 1 : -1, abs(rb), motors.get_adj_lag(RB_MOTOR, lag));
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
