/**
 * @file box.ino
 * @brief Arduino Uno firmware for directional visual feedback using a LED box.
 *
 * This sketch controls six LEDs mounted in a physical box that provide directional
 * and compression-depth feedback to the user. Commands are received via Serial (115200 baud)
 * and each token (e.g., "UP", "HARDER") maps to a specific LED activation.
 *
 * ## Feedback Design
 * - **Directional Cues**:
 *   - "UP", "DOWN", "LEFT", "RIGHT" turn on one directional LED.
 *   - These indicate correction in hand position.
 * - **Depth Cues**:
 *   - "HARDER" (compress deeper) → Activates depth LED for HARDER
 *   - "WEAKER" (compress shallower) → Activates depth LED for WEAKER
 *   - These LEDs turn off automatically after a configurable timeout.
 * - "OFF" turns off all directional LEDs.
 *
 * ## Pin Mapping
 * - Directional LEDs: Pins 2–5
 * - Depth LEDs: Pins 6–7
 *   ```
 *   2: UP
 *   3: DOWN
 *   4: RIGHT
 *   5: LEFT
 *   6: WEAKER
 *   7: HARDER
 *   ```

 * ## Behavior
 * - Supports comma-separated command strings (e.g., `"UP,HARDER"`)
 * - Directional LEDs clear immediately before a new position command
 * - Depth LEDs auto-clear after `DEPTH_LED_DURATION` (default: 1000 ms)
 */

// led pins
const uint8_t PIN_UP     = 2;
const uint8_t PIN_DOWN   = 3;
const uint8_t PIN_RIGHT  = 4;
const uint8_t PIN_LEFT   = 5;
const uint8_t PIN_WEAKER = 6;
const uint8_t PIN_HARDER = 7;

// how long to hold depth LEDs (ms)
const unsigned long DEPTH_LED_DURATION = 1000;

unsigned long lastDepthCmdTime = 0;
bool depthLedActive         = false;

// helper: turn all position/depth LEDs off
void allOff() {
  digitalWrite(PIN_UP,     LOW);
  digitalWrite(PIN_DOWN,   LOW);
  digitalWrite(PIN_RIGHT,  LOW);
  digitalWrite(PIN_LEFT,   LOW);
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(10);  // readStringUntil waits max 10 ms

  pinMode(PIN_UP,     OUTPUT);
  pinMode(PIN_DOWN,   OUTPUT);
  pinMode(PIN_RIGHT,  OUTPUT);
  pinMode(PIN_LEFT,   OUTPUT);
  pinMode(PIN_WEAKER, OUTPUT);
  pinMode(PIN_HARDER, OUTPUT);
  allOff();
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();

    bool containsPosition = line.indexOf("UP") >= 0 || line.indexOf("DOWN") >= 0 ||
                            line.indexOf("LEFT") >= 0 || line.indexOf("RIGHT") >= 0;

    // clear ONLY position leds if any position tokens exist
    if (containsPosition) {
      digitalWrite(PIN_UP,   LOW);
      digitalWrite(PIN_DOWN, LOW);
      digitalWrite(PIN_LEFT, LOW);
      digitalWrite(PIN_RIGHT, LOW);
    }

    // depth leds are cleared by timer

    int pos = 0;
    while (pos < line.length()) {
      int comma = line.indexOf(',', pos);
      String token = (comma < 0) ? line.substring(pos) : line.substring(pos, comma);
      pos = (comma < 0) ? line.length() : comma + 1;
      token.trim();

      if (token.equalsIgnoreCase("HARDER")) {
        digitalWrite(PIN_HARDER, HIGH);
        lastDepthCmdTime = millis();
        depthLedActive = true;
      }
      else if (token.equalsIgnoreCase("WEAKER")) {
        digitalWrite(PIN_WEAKER, HIGH);
        lastDepthCmdTime = millis();
        depthLedActive = true;
      }
      else if (token.equalsIgnoreCase("UP")) {
        digitalWrite(PIN_UP, HIGH);
      }
      else if (token.equalsIgnoreCase("DOWN")) {
        digitalWrite(PIN_DOWN, HIGH);
      }
      else if (token.equalsIgnoreCase("LEFT")) {
        digitalWrite(PIN_LEFT, HIGH);
      }
      else if (token.equalsIgnoreCase("RIGHT")) {
        digitalWrite(PIN_RIGHT, HIGH);
      }
      else if (token.equalsIgnoreCase("OFF")) {
        allOff();
      }
    }
  }

  // auto‐turn‐off depth LEDs after the duration elapses
  if (depthLedActive && (millis() - lastDepthCmdTime >= DEPTH_LED_DURATION)) {
    digitalWrite(PIN_HARDER, LOW);
    digitalWrite(PIN_WEAKER, LOW);
    depthLedActive = false;
  }

  delay(1);
}