/**
 * @file glove.ino
 * @brief Arduino Uno firmware for directional haptic feedback using a glove.
 *
 * This sketch controls four vibration motors and four LEDs mounted on a glove to
 * provide real-time CPR feedback cues based on directional error or compression quality.
 * Commands are received over Serial (115200 baud) and translated into motor/LED activations.
 *
 * ## Orientation
 * The orientation assumes the CPR performer is kneeling on the right side of the patient,
 * and the glove is worn on the right hand pointing across the chest.
 *
 * ## Feedback Mapping
 * | Command  | Activated Actuator |
 * |----------|---------------------|
 * | "UP"     | North motor + LED   |
 * | "DOWN"   | South motor + LED   |
 * | "LEFT"   | West motor + LED    |
 * | "RIGHT"  | East motor + LED    |
 * | "HARDER" | All motors + LEDs   |
 * | "OFF"    | Deactivates all     |
 *
 * ## Pin Configuration
 * Adjust these constants based on physical glove wiring:
 * - Motors: pins 4, 5, 6, 7
 * - LEDs:   pins 8, 9, 10, 11
 *
 * ## Serial Protocol
 * - Commands are sent as comma-separated strings (e.g., `"UP"`, `"RIGHT,DOWN"`, `"OFF"`)
 * - All commands are case-insensitive and processed immediately
 *
 * Author: [Your Name]
 * Date: [Thesis Year]
 */


// This mapping is in speicifc orientation where the CPR performer is on the right side of the person and the fingers pointing across the chest.
const uint8_t PIN_NORTH_MOTOR = 4;
const uint8_t PIN_EAST_MOTOR  = 5;
const uint8_t PIN_SOUTH_MOTOR = 7;
const uint8_t PIN_WEST_MOTOR  = 6;

const uint8_t PIN_NORTH_LED   = 8;
const uint8_t PIN_EAST_LED    = 9;
const uint8_t PIN_SOUTH_LED   = 11;
const uint8_t PIN_WEST_LED    = 10;

// helper to turn all actuators off
void allOff() {
  digitalWrite(PIN_NORTH_LED, LOW);
  digitalWrite(PIN_EAST_LED,  LOW);
  digitalWrite(PIN_SOUTH_LED, LOW);
  digitalWrite(PIN_WEST_LED,  LOW);

  digitalWrite(PIN_NORTH_MOTOR, LOW);
  digitalWrite(PIN_EAST_MOTOR,  LOW);
  digitalWrite(PIN_SOUTH_MOTOR, LOW);
  digitalWrite(PIN_WEST_MOTOR,  LOW);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);

  pinMode(PIN_NORTH_LED, OUTPUT);
  pinMode(PIN_EAST_LED,  OUTPUT);
  pinMode(PIN_SOUTH_LED, OUTPUT);
  pinMode(PIN_WEST_LED,  OUTPUT);

  pinMode(PIN_NORTH_MOTOR, OUTPUT);
  pinMode(PIN_EAST_MOTOR,  OUTPUT);
  pinMode(PIN_SOUTH_MOTOR, OUTPUT);
  pinMode(PIN_WEST_MOTOR,  OUTPUT);

  allOff();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    allOff();  // clear state before applying new command

    int pos = 0;
    while (pos < line.length()) {
      int comma = line.indexOf(',', pos);
      String token = (comma == -1) ? line.substring(pos) : line.substring(pos, comma);
      pos = (comma == -1) ? line.length() : comma + 1;
      token.trim();

      if (token.equalsIgnoreCase("UP")) {
        digitalWrite(PIN_NORTH_LED,   HIGH);
        digitalWrite(PIN_NORTH_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("DOWN")) {
        digitalWrite(PIN_SOUTH_LED,   HIGH);
        digitalWrite(PIN_SOUTH_MOTOR, HIGH);
      } else if (token.equalsIgnoreCase("LEFT")) {
        digitalWrite(PIN_WEST_LED,    HIGH);
        digitalWrite(PIN_WEST_MOTOR,  HIGH);
      } else if (token.equalsIgnoreCase("RIGHT")) {
        digitalWrite(PIN_EAST_LED,    HIGH);
        digitalWrite(PIN_EAST_MOTOR,  HIGH);
      } else if (token.equalsIgnoreCase("HARDER")) {
        digitalWrite(PIN_NORTH_LED,   HIGH);
        digitalWrite(PIN_NORTH_MOTOR, HIGH);
        digitalWrite(PIN_SOUTH_LED,   HIGH);
        digitalWrite(PIN_SOUTH_MOTOR, HIGH);
        digitalWrite(PIN_WEST_LED,    HIGH);
        digitalWrite(PIN_WEST_MOTOR,  HIGH);
        digitalWrite(PIN_EAST_LED,    HIGH);
        digitalWrite(PIN_EAST_MOTOR,  HIGH);
      } else if (token.equalsIgnoreCase("OFF")) {
        allOff();
      }
      // ignore unknown tokens
    }
  }

  delay(1);
}