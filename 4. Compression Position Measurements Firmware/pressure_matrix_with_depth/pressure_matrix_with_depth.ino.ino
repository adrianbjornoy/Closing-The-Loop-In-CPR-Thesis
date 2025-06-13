/**
 * @file pressure_matrix_with_depth.ino
 * @brief Arduino Mega code for reading a 12x12 pressure matrix and depth from Arduino Nano.
 *
 * This sketch reads data from a resistive pressure matrix and synchronizes with a
 * secondary Arduino Nano to record compression depth. It supports a full 12x12 matrix
 * layout, though the current hardware setup uses a 12x10 layout. The code is forward-
 * compatible with 12x12 and still functions correctly even if fewer rows are populated.
 *
 * Features:
 * - Scans a pressure matrix via analog rows and digital columns
 * - Applies exponential smoothing to reduce noise (`alpha` filter)
 * - Baseline calibration on startup to subtract ambient pressure
 * - Reads depth signal from Arduino Nano over Serial1 (via command `RD`)
 * - Streams full sensor matrix and depth values to Serial (USB) for visualization/logging
 *
 * Matrix Layout:
 * - Rows: A0–A11 (analog inputs)
 * - Columns: 22–44 (digital outputs, even pins)
 * - Matrix values are printed row-by-row, comma-separated
 * - A depth value from Nano is printed prefixed with `D,` on its own line
 *
 * Output Format:
 * ```
 * val00,val01,...,val011
 * val10,val11,...,val111
 * ...
 * D,<depth_value>
 *
 * ```
 * (blank line used to separate each matrix+depth packet)
 */

// Define the number of rows and columns in the matrix
const int numRows = 12;
const int numCols = 12; 

// Define the pin numbers for rows and columns
const int rowPins[numRows] = {A0, A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, A11};  // Analog pins connected to rows
const int colPins[numCols] = {22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44};   // Digital pins connected to columns

// 2D array to hold sensor values
float sensorMatrix[numRows][numCols];

const float alpha = 0.2; // smoothing factor (0.1 = more stable, 0.5 = more reactive)

float baselineMatrix[numRows][numCols]; // stores initial baseline values

void calibrateBaseline() {
  for (int col = 0; col < numCols; col++) {
    digitalWrite(colPins[col], HIGH);
    delayMicroseconds(10);

    for (int row = 0; row < numRows; row++) {
      float total = 0;
      for (int i = 0; i < 5; i++) { // take multiple samples for stability
        total += analogRead(rowPins[row]);
        delayMicroseconds(5);
      }
      baselineMatrix[row][col] = total / 5.0; // average baseline value
    }

    digitalWrite(colPins[col], LOW);
  }
}

void setup() {
  for (int row = 0; row < numRows; row++) pinMode(rowPins[row], INPUT);
  for (int col = 0; col < numCols; col++) {
    pinMode(colPins[col], OUTPUT);
    digitalWrite(colPins[col], LOW);
  }
  
  Serial.begin(115200);      // USB to PC
  Serial1.begin(115200);     // Nano connection on Serial1 (pins 19/18)
  calibrateBaseline(); // Zero calibration at boot
}

void loop() {
  // Collect sensor values into the matrix
  for (int col = 0; col < numCols; col++) {
    digitalWrite(colPins[col], HIGH);
    delayMicroseconds(10); // Short delay to stabilize the signal

    for (int row = 0; row < numRows; row++) {
      int adcValue = analogRead(rowPins[row]);
      float filteredValue = max(0, adcValue - baselineMatrix[row][col]);
      sensorMatrix[row][col] = alpha * filteredValue + (1 - alpha) * sensorMatrix[row][col];
    }

    digitalWrite(colPins[col], LOW);
  }

  // Output matrix and possibly compression
  sendMatrixAndCompression();

  delay(100);  // Small delay before next reading
}

void sendMatrixAndCompression() {
  // send the matrix
  for (int row = 0; row < numRows; row++) {
    for (int col = 0; col < numCols; col++) {
      Serial.print(sensorMatrix[row][col], 2); // Two decimal places
      if (col < numCols - 1) {
        Serial.print(",");  // Column separator
      }
    }
    Serial.println();  // Row separator
  }

  // ask nano for compression event
  Serial1.println("RD");

  unsigned long timeout = millis();
  while (Serial1.available() == 0 && (millis() - timeout) < 5) {
    // wait max 5ms for nano to reply
  }

  if (Serial1.available()) {
    String line = Serial1.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      Serial.print("D,");
      Serial.println(line);
    }
  }

  Serial.println();  // Separator (blank line) after every matrix block
}

