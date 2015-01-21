#include "SerialCommand.h"
#include <Wire.h>

SerialCommand comm;

enum MOTORS {
  LEFT_ENGINE = 0,
  RIGHT_ENGINE,
  KICKER,
  MAX_ENGINES
};

float MAX_SPEED = 1; // TODO: get real value, etc

bool IS_KICKING = false;

void setup() {
  Serial.begin(115200);  // 115kb
  // test function
  comm.addCommand("A_BLINK", my_blink);
  
  // performs a kick
  comm.addCommand("A_KICK", kick);
  /*
  // might want this, depending on design
  comm.addCommand("A_CATCH", catch);
  */
  // sets two speed/accel values for movement engines
  comm.addCommand("A_SET_MOVE", set_movement);
  comm.addCommand("A_RUN_MOVE", run_movement);
  
  // sets speed/accel values for a given engine
  // format A_SET_ENGINE ENG_ID float
  comm.addCommand("A_SET_ENGINE", set_engine_parse);
  comm.addCommand("A_RUN_ENGINE", run_engine_parse);
  comm.addDefaultHandler(invalid_command);
  
  // for LED
  pinMode(13, OUTPUT);
}

void invalid_command() {
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

void loop() {
  if (IS_KICKING) {
    Serial.flush();
  } else {
    comm.readSerial();
  }
  /* TODO: if kicking is done, reset kicker */
  // parsing stuff out every 100ms for debug
  delay(100);
}

void kick() {
  // activate relevant engine
  set_engine(KICKER, MAX_SPEED);
  IS_KICKING = true;
}

/* pushing this as a utility as it's used quite often */
bool get_float(float &first) {
  char *tmp = comm.next();
  if (!tmp) return false;
  first = atof(tmp);
  return true;
}

bool get_int(int &first) {
  char *tmp = comm.next();
  if (!tmp) return false;
  first = atoi(tmp);
  return true;
}

/* sets velocities */
void set_movement() {
  float left, right;
  if (!get_float(left) || !get_float(right)) {
    //TODO: signal error?
    return;
  }
  set_engine(LEFT_ENGINE, left);
  set_engine(RIGHT_ENGINE, right);
  return;
}

/* sets distance (clicks or whatever) */
void run_movement() {
  float left, right;
  if (!get_float(left) || !get_float(right)) {
    //TODO: signal error?
    return;
  }
  run_engine(LEFT_ENGINE, left);
  run_engine(RIGHT_ENGINE, right);
}

/* parses set_engine parameters from comm */
void set_engine_parse() {
  int id;
  float value;
  // don't need to free these pointers as they aren't really allocated
  if (!get_int(id) || !get_float(value)) {
    // TODO: signal error?
    return;
  }
  set_engine(id, value);
  return;
}

/* parses run_engine parameters from comm */
void run_engine_parse() {
  int id;
  float value;
  // don't need to free these pointers as they aren't really allocated
  if (!get_int(id) || !get_float(value)) {
    // TODO: signal error?
    return;
  }
  run_engine(id, value);
  return;
}

/*
  sets speed/accel for a given engine
  also checks whether arguments are correct
*/
void set_engine(int id, float value) {
  float val = abs(value);
  if (id < 0 || id >= MAX_ENGINES || val > MAX_SPEED) {
    // TODO: error reporting
    return;
  }
  // parameters are fine here, just push it all to a correct engine
  // depends on what we should be using for motor-stuff
}

/*
  sets the distance [clicks, whatever] to run for a given engine
*/
void run_engine(int id, float value) {
  if (id < 0 || id >= MAX_ENGINES || value < 0) {
    // TODO: error reporting
    return;
  }
  // push distances to correct engine
}
