#include <Arduino.h>
#include <Wire.h>
#include "SDPMotors.h"

#define MotorBoardI2CAddress 4
MotorBoard::MotorBoard(): stop_timers() {
  for (int i = 0; i < MAX_ENGINES_BOARD; i++)
    start_timers[i] = -1;
  last_check = millis();
}

void MotorBoard::run_motor(uint8_t id, float power, uint16_t duration, int16_t start_at ) {
  if (id >= 0 && id < MAX_ENGINES_BOARD) {
#ifdef DEBUG
    Serial.print("Trying to run motor ");
    Serial.print(id);
    Serial.print(", power ");
    Serial.print(power);
    Serial.print(", stops in ");
    Serial.print(duration + ENGINE_ACTIVATION[id]);
    Serial.print(", added lag ");
    Serial.print(start_at);
    Serial.print(", duration ");
    Serial.println(duration);
    Serial.flush();
#endif
    if (start_at > 0) {
      start_timers[id] = start_at;
      stop_timers[id] = duration;
      powers[id] = power;
      return;
    }
    start_timers[id] = -1;
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
    stop_timers[id] = duration;
    if (start_at == 0)
      stop_timers[id] += ENGINE_ACTIVATION[id];
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
    start_timers[id] = -1;
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
    if (stop_timers[i] > 0) { // motor hasn't stopped
      if (start_timers[i] < 0) { // it started
        if (stop_timers[i] > diff)
          stop_timers[i] -= diff;
        else {
          stop_motor(i);
          stop_timers[i] = 0;
        }
      }
      else { // it hasn't started running
        if (start_timers[i] > diff)
          start_timers[i] -= diff;
        else {
          start_timers[i] = -1;
          run_motor(i, powers[i], stop_timers[i], 0);
        }
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
      run_motor(i, 0.5, 500, 0);
      delay(500);
      stop_motor(i);
      run_motor(i, -0.5, 500,0);
      delay(500);
      stop_motor(i);
    }
  }
#ifdef DEBUG
  Serial.println("Diagnostics finished");
#endif
}

uint16_t MotorBoard::get_max_lag(uint8_t mask[], uint8_t count) {
  uint16_t max_lag = 0;
  for (int i = 0; i < count; i++) { 
    if (max_lag < ENGINE_ACTIVATION[mask[i]]) {
      max_lag = ENGINE_ACTIVATION[mask[i]];
    }
  }
  return max_lag;
}

uint16_t MotorBoard::get_adj_lag(uint8_t id, int16_t d) {
  int16_t lag = d - ENGINE_ACTIVATION[id];
  if (lag < 0)
    return 0;
  return (uint16_t)lag;
}
