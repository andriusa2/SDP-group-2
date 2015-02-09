#include <Arduino.h>
#include <Wire.h>
#include "SDPMotors.h"

#define MotorBoardI2CAddress 4
// get these manually
static uint16_t ENGINE_ACTIVATION[] = {110, 0, 0, 50, 90, 0};
MotorBoard::MotorBoard(): stop_timers() {
  last_check = millis();
}

void MotorBoard::run_motor(uint8_t id, float power, uint16_t duration) {
  if (id >= 0 && id < MAX_ENGINES_BOARD) {
#ifdef DEBUG
    Serial.print("Trying to run motor ");
    Serial.print(id);
    Serial.print(", power ");
    Serial.print(power);
    Serial.print(", stops in ");
    Serial.print(duration + ENGINE_ACTIVATION[id]);
    Serial.print(", duration ");
    Serial.println(duration);
#endif
    // clamp power to [-1.0;1.0]
    if (power < -1.0) power = -1.0;
    else if (power > 1.0) power = 1.0;
    // fwd is 2, bwd is 3
    byte mode = 2;
    if (power < 0.0) {
      mode = 3;
      power = -power;
    }
    // hopefully arduino compiler is smart enough
    const byte motorCmd = id << 5 | 24 | mode << 1;
    const byte payload = int(power * 255.);
    byte send[2] = {motorCmd, payload};
    // open connection
    Wire.beginTransmission(MotorBoardI2CAddress);
    // send 2B of data
    Wire.write(send, 2);
    Wire.endTransmission();  // retval ignored
    stop_timers[id] = duration + ENGINE_ACTIVATION[id];
#ifdef DEBUG
    Serial.println("Done");
#endif
  }
}

void MotorBoard::stop_motor(uint8_t id) {
  if (id >= 0 && id < MAX_ENGINES_BOARD) {
#ifdef DEBUG
    Serial.print("Trying to stop motor: ");
    Serial.println(id);
#endif
    // id << 5 | 16 | 0 << 1
    byte cmd = id << 5 | 16;
    Wire.beginTransmission(MotorBoardI2CAddress);
    Wire.write(&cmd, 1);
    Wire.endTransmission();
    stop_timers[id] = 0;
#ifdef DEBUG
    Serial.print("Stopped motor: ");
    Serial.println(id);
#endif
  }
}

void MotorBoard::stop_all() {
#ifdef DEBUG
  Serial.println("Trying to stop all motors");
#endif
  byte cmd = 1;
  Wire.beginTransmission(MotorBoardI2CAddress);
  Wire.write(&cmd, 1);
  Wire.endTransmission();
  for (byte i = 0; i < MAX_ENGINES_BOARD; i++)
    stop_timers[i] = 0;
#ifdef DEBUG
  Serial.println("Stopped all motors");
#endif
}

/* checks whether some motor is to be stopped */
void MotorBoard::scan_motors() {
  const uint32_t now = millis();
  // will overflow every 50 days or so according to manual
  const uint32_t diff = now - last_check;
  last_check = now;
  for (byte i = 0; i < MAX_ENGINES_BOARD; i++)
    if (stop_timers[i] > 0) {
      if (stop_timers[i] > diff)
        stop_timers[i] -= diff;
      else {
        stop_motor(i);
      }
    }
}

void MotorBoard::diagnostics(uint8_t bitmask) {
#ifdef DEBUG
  Serial.println("Running diagnostics");
#endif
  for (int i = 0, m = 1; i < MAX_ENGINES_BOARD; i++, m <<= 1) {
    if (bitmask & m) {
      stop_motor(i);
      run_motor(i, 0.5, 500);
      delay(500);
      stop_motor(i);
      run_motor(i, -0.5, 500);
      delay(500);
      stop_motor(i);
    }
  }
#ifdef DEBUG
  Serial.println("Diagnostics finished");
#endif
}
    
