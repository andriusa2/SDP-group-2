// well... Might be more, but easiest to implement now
#define MAX_ENGINES_BOARD 6

//#define DEBUG

class MotorBoard {
public:
  MotorBoard();
  void run_motor(uint8_t id, float power, uint16_t duration);
  void stop_motor(uint8_t id);
  void stop_all();
  void diagnostics(uint8_t motor_bitmask);
  void scan_motors();
  bool is_running(uint8_t id) { return (id >= 0 && id < MAX_ENGINES_BOARD) ? stop_timers[id] > 0 : false; }
private:
  uint16_t stop_timers[MAX_ENGINES_BOARD];
  uint32_t last_check;
};
