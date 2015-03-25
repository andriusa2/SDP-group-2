#include "SDPMotors.h"
#include <Wire.h>
// determines the direction of "outwards" movement
#define KICK_POWER 1
#define GRAB_POWER -1
// determines durations at max power
#define KICK_DURATION 190
#define GRAB_DURATION 200

#define ACK_COMMS
#define DO_PARITY
// intermediate state
#define HAPPENING 1
// finished state
#define COMPLETE 2
// negative intermediate state
#define CLOSING 3

#define BUFF_SIZE 32
uint8_t buffer[BUFF_SIZE] = "";
uint8_t buff_head = 0;
uint8_t READY = 1;
uint8_t MATCHED_CMD = 0;
uint32_t LAST_CMD_PARAMS = 0;
long LAST_MATCH_TIME = 0;
MotorBoard motors;

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
void parse_packet();
void read_serial() {
  MATCHED_CMD = 0;
  while(Serial.available() > 0) {
    char a = Serial.read();
    if (a != '\t') {
      switch (buff_head) {
      case 0: break;
      case 1:
        if (a <= 'Z' && a >= 'A')
          buffer[buff_head++] = a;
        else buff_head = 0;
        break;  // reject impossible things
      default: buffer[buff_head++] = a;
      }
    }
    else {
      switch(buff_head) {
      case 0: buffer[buff_head++] = a; break;  // init hit
      case 1:
      case 5:
      case 6:
      case 10: buffer[buff_head++] = a; parse_packet(); break; // finishing byte
      // longest packet is 11B long, if we somehow reach this, just reset it all
      default: if (buff_head >= 11) buff_head = 0; buffer[buff_head++] = a; break;
      }
    }
    buffer[buff_head] = 0;
    if (buff_head >= BUFF_SIZE) buff_head = 0;
    if (MATCHED_CMD != 0) 
      while(Serial.available() > 0) Serial.read();
    MATCHED_CMD = 0;
  }
}

/*
Packet format:
0x00(K|F|L|T|O|C|S)BBP0x00  [6B]
where B is a byte, P is parity byte (xor'd Bs + 0)
0x00VBBBBBBBB0x00 [11B]
0x00RBBBB0x00 [7B]
0x000x00  -> heartbeat
When packet is identified it will be sent to a function to do things
and then acknowledged.
*/

void parse_packet() {
  // uses static buffer ^^^^
  if (buff_head <= 1) return;
  if ((char)buffer[0] != '\t' || buff_head >= BUFF_SIZE){ buff_head = 0; return;}
  if ((char)buffer[buff_head - 1] != '\t') return;
  uint8_t b = buff_head;
  buff_head = 0;
  switch(b) {
  case 2:
    // empty message, retransmit READY if needed
    if (READY != 0) {
      Serial.println("READY");
      Serial.flush();
    }
    return;
  case 6: {
    // command message, extract relevant parts and stuff to handler
    char cmd = buffer[1];
    if (cmd == 'V' || cmd == 'R') {
      buff_head = b;
      return;
    }
    uint8_t b1 = buffer[2], b2 = buffer[3];
    uint8_t p = b1 ^ b2 ^ 0;
    if (p != (byte)buffer[4]) {
      Serial.print("FAIL: Parity fail, got ");
      Serial.print(p);
      Serial.print(", but expected: ");
      Serial.println((byte)buffer[4]);
      Serial.flush();
      return;
    }
    // parity passed, handle it now
    command(cmd, b1, b2);
    Serial.println("ACK");
    Serial.flush();
    return;
  }
  case 7: {
    // run engine message, no parity
    char cmd = buffer[1];
    uint8_t id = buffer[2];
    int8_t pwr = buffer[3];
    // reinterpret_cast<int16_t>(buffer[4]) -> 4;5
    int16_t duration = *(int16_t*)(&buffer[4]);
    if (cmd != 'R') {
      if (cmd == 'V') {
        buff_head = b;
        return;
      }
      Serial.println("FAIL: Got run engine-like packet, but cmd isn't R, wat");
      return;
    }
    run_engine(id, pwr, duration);
    Serial.println("ACK");
    Serial.flush();
    return;
  }
  case 11: {
    // full move message, no parity
    char cmd = buffer[1];
    int16_t lf = *(int16_t*)(&buffer[2]);
    int16_t rf = *(int16_t*)(&buffer[4]);
    int16_t lb = *(int16_t*)(&buffer[6]);
    int16_t rb = *(int16_t*)(&buffer[8]);
    if (cmd != 'M') {
      Serial.println("FAIL: Got move-like packet, but cmd isn't M, wat");
      return;
    }
    move_bot(lf, rf, lb, rb);
    Serial.println("ACK");
    Serial.flush();
    return;
  }
  default:
    Serial.print("FAIL: Got msg:");
    Serial.println((char*)buffer + 1);
    Serial.flush();
    return;
  }
}

void setup() {
  Serial.begin(115200);  // 115kb
  setup_pins();
  Wire.begin();  // need this s.t. arduino is mastah
  Serial.println("Team2READY");
  Serial.flush();
  motors.stop_all();
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
  if (READY == 0 && motors.all_stopped())
    READY = 1;
  read_serial();
  delay(5);
}

void command(char cmd, uint8_t b1, uint8_t b2) {
  MATCHED_CMD = 1;
  uint8_t cd[] = {cmd, b1, b2, 0};
  uint32_t last_cmd = LAST_CMD_PARAMS;
  uint32_t last_time = LAST_MATCH_TIME;
  uint32_t LAST_CMD_PARAMS = *(uint32_t*)(&cd[0]);
  long LAST_MATCH_TIME = millis();
  if (last_cmd == LAST_CMD_PARAMS && LAST_MATCH_TIME - last_time < 1000) {
    return;
  }
  switch (cmd) {
  case 'K': kick(b1); READY = 0; return;
  case 'F': move_front(b1, b2);  READY = 0;return;
  case 'L': move_left(b1, b2);  READY = 0;return;
  case 'T': turn(b1, b2);  READY = 0;return;
  case 'O': grab_open(b1);  READY = 0;return;
  case 'C': grab_close(b1);  READY = 0;return;
  case 'S': stop_engines(); READY = 0; return;
  default: READY = 1; MATCHED_CMD = 0;
  }
}
int16_t reint(uint8_t a, uint8_t b) {
  // I am aware that I could try to mess with &a and &b, but no. Just no.
  uint8_t tmp[] = {a, b};
  return *(int16_t*)(&tmp);
}
void move_front(uint8_t a, uint8_t b) {
  if (READY == 0) return;
  int16_t d = reint(a, b);
  return move_bot(d, d, d, d);
}
void move_left(uint8_t a, uint8_t b) {
  if (READY == 0) return;
  int16_t d = reint(a, b);
  return move_bot(-d, d, d, -d);
}
void turn(uint8_t a, uint8_t b) {
  if (READY == 0) return;
  int16_t d = reint(a, b);
  return move_bot(d, d, -d, -d);
}

void stop_engines() {
  // only stops movement engines!
  motors.stop_motor(LF_MOTOR);
  motors.stop_motor(LB_MOTOR);
  motors.stop_motor(RF_MOTOR);
  motors.stop_motor(RB_MOTOR);
}

/* KICK [POWER(0;1]=1] */
void kick(uint8_t pwr) {
  MATCHED=1;
  if (IS_GRABBER_OPEN == COMPLETE) {
    
    float power = float(pwr) / 255.0;
    
    kick_f(power * KICK_POWER);
  }
  else {
    grab_open(255);
    KICK_AFTERWARDS = 1;
  }
}

// OPEN GRABBER
void grab_open(uint8_t pwr) {
  float power = float(pwr) / 255.0;
  if (IS_GRABBER_OPEN != 0)
    return;
  IS_GRABBER_OPEN = HAPPENING;
  motors.run_motor(GRABBER, power * GRAB_POWER, uint16_t(float(GRAB_DURATION) / power), 0);
}
// close grab
void grab_close(uint8_t pwr) {
  float power = float(pwr) / 255.0;
  if (IS_GRABBER_OPEN != COMPLETE)
    return;
  IS_GRABBER_OPEN = CLOSING;
  motors.run_motor(GRABBER, -power * GRAB_POWER, uint16_t(float(GRAB_DURATION) / power), 0);
}

void move_bot(int16_t lf, int16_t lb, int16_t rf, int16_t rb) {
  if (READY == 0) return;
  uint16_t lag = motors.get_max_lag(movement_motors, 4);
  motors.run_motor(LF_MOTOR, lf > 0? 1 : -1, abs(lf), motors.get_adj_lag(LF_MOTOR, lag));
  motors.run_motor(LB_MOTOR, lb > 0? 1 : -1, abs(lb), motors.get_adj_lag(LB_MOTOR, lag));
  motors.run_motor(RF_MOTOR, rf > 0? 1 : -1, abs(rf), motors.get_adj_lag(RF_MOTOR, lag));
  motors.run_motor(RB_MOTOR, rb > 0? 1 : -1, abs(rb), motors.get_adj_lag(RB_MOTOR, lag));
}

void run_engine(uint8_t id, int8_t pwr, uint16_t time) {
  float power = float(pwr) / 127.0;
  motors.run_motor(id, power, time, -1);
}


