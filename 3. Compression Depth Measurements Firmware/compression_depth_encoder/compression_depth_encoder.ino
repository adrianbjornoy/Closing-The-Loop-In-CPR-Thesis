/**
 * @file compression_depth_encoder.ino
 * @brief Arduino Nano code to measure compression depth using a rotary encoder (AS5047P).
 *
 * This sketch uses an AS5047P magnetic rotary encoder to track linear displacement
 * during CPR compressions, converting rotational angle to millimeter depth.
 * It detects compression events, extracts peak depth, and reports the data
 * when requested by a master device over serial.
 *
 * Features:
 * - Converts angle readings to linear depth using a fixed conversion factor
 * - Unwraps angle to handle multiple revolutions
 * - Detects compression start/end based on configurable thresholds
 * - On receiving the command `"RD"` over Serial, returns:
 *     - Max depth of the last completed compression
 *     - Timestamp (ms since boot) when the compression ended
 *
 * Communication Protocol:
 * - Input: "RD" command over Serial (USB or UART from Mega)
 * - Output: If a compression has occurred:
 *     `depth_mm,timestamp\n`
 *   Otherwise:
 *     `\n` (blank line to indicate no new event)
 *
 * Constants:
 * - `DEG2MM`: conversion factor from angle (degrees) to millimeters
 * - `COMP_START_THRESHOLD`: depth (mm) to consider start of a compression
 * - `COMP_END_THRESHOLD`: depth (mm) to consider end of a compression
 *
 * Dependencies:
 * - Requires AS5047P library
 */

#include <AS5047P.h>

#define AS5047P_CHIP_SELECT_PORT 10
#define AS5047P_CUSTOM_SPI_BUS_SPEED 1000000

AS5047P as5047p(AS5047P_CHIP_SELECT_PORT, AS5047P_CUSTOM_SPI_BUS_SPEED);

const float DEG2MM = 0.044;
const float COMP_START_THRESHOLD = 15.0;
const float COMP_END_THRESHOLD = 5.0;

float last_angle = 0;
float total_angle = 0;
bool in_compression = false;

float max_depth = 0;
unsigned long comp_end_time = 0;
bool compression_ready = false;

float unwrap_angle(float current_angle) {
  float delta = current_angle - last_angle;
  if (delta > 180) delta -= 360;
  if (delta < -180) delta += 360;
  last_angle = current_angle;
  total_angle += delta;
  return total_angle;
}

void setup() {
  Serial.begin(115200);
  while (!as5047p.initSPI()) {
    delay(1000);
  }

  float angle_sum = 0;
  for (int i = 0; i < 20; i++) {
    angle_sum += as5047p.readAngleDegree();
    delay(5);
  }
  last_angle = angle_sum / 20;
  total_angle = 0;
}

void loop() {
  float raw_angle = as5047p.readAngleDegree();
  float unwrapped = unwrap_angle(raw_angle);
  float depth_mm = unwrapped * DEG2MM;

  // compression logic
  if (!in_compression && depth_mm > COMP_START_THRESHOLD) {
    in_compression = true;
    max_depth = depth_mm;
  } else if (in_compression) {
    if (depth_mm > max_depth) max_depth = depth_mm;
    if (depth_mm < COMP_END_THRESHOLD) {
      in_compression = false;
      comp_end_time = millis();
      compression_ready = true;
    }
  }

  // check for read request
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim(); // just in case

    if (cmd == "RD") {
      if (compression_ready) {
        Serial.print(max_depth, 2);
        Serial.print(",");
        Serial.println(comp_end_time);
        compression_ready = false; // mark as sent
      } else {
        Serial.println(); // empty response = no new data
      }
    }
  }
}
