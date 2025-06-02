/**
 * @file belt.ino
 * @brief Arduino Uno firmware for delivering CPR feedback through vibration motors mounted on a belt.
 *
 * This sketch provides haptic feedback using vibration motors to guide the CPR performer
 * during compressions. The feedback includes both positional and depth corrections,
 * communicated via Serial commands.
 *
 * ## Feedback Design
 * - **Positional Feedback**:
 *   - Directional cues ("UP", "DOWN", "LEFT", "RIGHT") activate corresponding motors.
 *   - Orientation assumes the CPR performer is on the right side of the patient,
 *     with the belt wrapped around the torso.
 *
 * - **Depth Feedback**:
 *   - "HARDER" → Vibrates a dedicated motor to indicate deeper compression needed.
 *   - "WEAKER" → Vibrates a different motor to indicate shallower compression.
 *
 * ## Pin Assignments (Current Physical Layout: Performer on Right Side)
 * ```
 * Directional Motors:
 *   4: LEFT (West)
 *   5: UP (North)
 *   6: RIGHT (East)
 *   7: DOWN (South)
 * Depth Motors:
 *   8: HARDER
 *   9: WEAKER
 * ```

 * ## Behavior
 * - Accepts Serial input strings like `"UP,HARDER"` (comma-separated tokens).
 * - Turns off all motors before every new command.
 * - Uses `Serial.setTimeout(10)` for fast command parsing.
 */

// This mapping is in speicifc orientation where the CPR performer is on the right side of the person and the fingers pointing across the chest.
const uint8_t PIN_NORTH_MOTOR = 5;  // UP
const uint8_t PIN_EAST_MOTOR  = 6;  // RIGHT
const uint8_t PIN_SOUTH_MOTOR = 7;  // DOWN
const uint8_t PIN_WEST_MOTOR  = 4;  // LEFT

const uint8_t PIN_HARDER_MOTOR = 8;  // HARDER
const uint8_t PIN_WEAKER_MOTOR  = 9;  // WEAKER

void allOff() {
  digitalWrite(PIN_NORTH_MOTOR, LOW);
  digitalWrite(PIN_EAST_MOTOR,  LOW);
  digitalWrite(PIN_SOUTH_MOTOR, LOW);
  digitalWrite(PIN_WEST_MOTOR,  LOW);
  digitalWrite(PIN_HARDER_MOTOR,  LOW);
  digitalWrite(PIN_WEAKER_MOTOR,  LOW);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);

  pinMode(PIN_NORTH_MOTOR, OUTPUT);
  pinMode(PIN_EAST_MOTOR,  OUTPUT);
  pinMode(PIN_SOUTH_MOTOR, OUTPUT);
  pinMode(PIN_WEST_MOTOR,  OUTPUT);
  pinMode(PIN_HARDER_MOTOR,  OUTPUT);
  pinMode(PIN_WEAKER_MOTOR,  OUTPUT);

  allOff();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    allOff();

    int pos = 0;
    while (pos < line.length()) {
      int comma = line.indexOf(',', pos);
      String token = (comma == -1) ? line.substring(pos) : line.substring(pos, comma);
      pos = (comma == -1) ? line.length() : comma + 1;
      token.trim();

      if (token.equalsIgnoreCase("UP")) {
        digitalWrite(PIN_NORTH_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("DOWN")) {
        digitalWrite(PIN_SOUTH_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("LEFT")) {
        digitalWrite(PIN_WEST_MOTOR,  HIGH);
      } else if (token.equalsIgnoreCase("RIGHT")) {
        digitalWrite(PIN_EAST_MOTOR,  HIGH);
      } else if (token.equalsIgnoreCase("HARDER")) {
        digitalWrite(PIN_HARDER_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("WEAKER")) {
        digitalWrite(PIN_WEAKER_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("OFF")) {
        allOff();
      }
    }
  }

  delay(1);
}
