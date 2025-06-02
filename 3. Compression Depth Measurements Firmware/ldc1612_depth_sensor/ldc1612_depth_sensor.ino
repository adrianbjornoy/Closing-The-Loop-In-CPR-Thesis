/**
 * @file ldc1612_depth_sensor.ino
 * @brief Measures CPR compression depth using an inductive sensor (LDC1612 and coil).
 *
 * This sketch reads raw inductance-based proximity data from an LDC1612 sensor connected
 * to an external coil. The distance (depth) is calculated using a linear mapping from
 * calibrated raw values to millimeters, and optionally smoothed using exponential filtering.
 *
 * Features:
 * - Uses I²C communication to interface with the LDC1612 inductive sensor
 * - Maps raw inductance values (`RAW_MIN` to `RAW_MAX`) to a depth range (0 to 55 mm)
 * - Applies exponential smoothing for stable output (`SMOOTH_ALPHA`)
 * - Outputs smoothed depth to Serial in human-readable format
 *
 * Calibration:
 * - `RAW_MIN`: raw sensor value when object is farthest (no compression)
 * - `RAW_MAX`: raw value at full compression (closest proximity)
 * - Adjust `DEPTH_MIN` and `DEPTH_MAX` if physical range changes
 *
 * Output Format:
 * ```
 * raw: <raw_value> | depth (mm): <smoothed_depth>
 * ```
 * - Sent over USB Serial at 115200 baud
 *
 * Dependencies:
 * - Requires Seeed LDC1612 library
 */

#include <Wire.h>
#include "Seeed_LDC1612.h"

LDC1612 sensor;

// calibration parameters
#define RAW_MIN  54859499  // raw value at farthest depth
#define RAW_MAX  55033714  // raw value at closest depth
#define DEPTH_MIN  0.0       // mm
#define DEPTH_MAX  55.0      // mm

#define SMOOTH_ALPHA 0.1     // 0 = no smoothing, 1 = infinite smoothing

float smoothedDepth = 0.0;

void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("ldc1612 depth from external coil");

  sensor.init();

  if (sensor.LDC1612_mutiple_channel_config()) {
    Serial.println("sensor init failed");
    while (1);
  }
}

void loop() {
  u32 raw = 0;
  if (sensor.get_channel_result(1, &raw) == 0 && raw > 0) {

    raw = constrain(raw, RAW_MIN, RAW_MAX);

    float norm = (float)(raw - RAW_MIN) / (RAW_MAX - RAW_MIN);
    float depth = DEPTH_MIN + norm * (DEPTH_MAX - DEPTH_MIN);

    smoothedDepth = SMOOTH_ALPHA * depth + (1 - SMOOTH_ALPHA) * smoothedDepth;

    Serial.print("raw: ");
    Serial.print(raw);
    Serial.print(" | depth (mm): ");
    Serial.println(smoothedDepth, 3);
  }

  delay(100);
}
