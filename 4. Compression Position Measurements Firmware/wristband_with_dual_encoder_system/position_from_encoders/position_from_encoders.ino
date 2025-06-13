/**
 * @file position_from_encoders.ino
 * @brief Calculates 2D position from two rotary encoders using string lengths.
 *
 * This Arduino sketch reads encoder counts from two serial-connected encoders,
 * which each spool string attached to a moving hand. Based on the length of string
 * spooled (derived from encoder ticks), it calculates the XY position of the hand
 * using basic triangulation equations.
 *
 * - Assumes encoders are mounted with a fixed horizontal distance `b` between them.
 * - Uses known spool diameter and steps per rotation to convert ticks to length.
 * - Outputs: X and Y position, along with L1 and L2 (string lengths from each encoder).
 * - Communication:
 *    - Input: Encoder data read from Serial1 and Serial2 (hardware serial ports).
 *    - Output: Position and lengths streamed via Serial (USB) in CSV format.
 *
 * Usage:
 *   1. Connect two encoders to Serial1 and Serial2.
 *   2. On startup, encoders must send their initial counts for zeroing.
 *   3. Position is printed over USB serial in the format: x,y,L1,L2\n
 *
 * Author: [Your Name]
 * Date: [Date or Thesis Year]
 */

const float dia = 23.3;
const int steps = 20;
const float pi = 3.14;
const float b = 300; // Distance between the two encoder mounts


struct Pos {
  float x;
  float y;
};

Pos position;

int inBytex = 0;
int inBytey = 0;

// Define offsets 
int offsetX = 0;
int offsetY = 0;

// Conversion function: encoder steps -> length
float rot2len(int pos){
  return (dia * pi * float(pos) / float(steps));
}

// Compute XY position from L1, L2

Pos calcPos(float L1, float L2){
  Pos pos;
  // From the derived equations:
  pos.x = ((L1*L1) - (L2*L2) + (b*b)) / (2*b);
  pos.y = sqrt((L1*L1) - (pos.x*pos.x));
  return pos;
}

void setup() {
  Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);
  //    Wait (briefly) for encoders to send data, then read them as offsets
  //    so that this position will be considered L1=0, L2=0.
  delay(1000); // Give encoders a moment to start sending
  if (Serial1.available() && Serial2.available()) {
    offsetX = Serial1.parseInt();  // the "zero" count for spool 1
    offsetY = Serial2.parseInt();  // the "zero" count for spool 2
  }
}

void loop() {
  // Read encoder values from Serial1 and Serial2
  if (Serial1.available()) {
    inBytex = Serial1.parseInt();  
  }
  if (Serial2.available()) {
    inBytey = Serial2.parseInt();  
  }

  // Only calculate position if both encoder counts are valid

  if (inBytex > 0 && inBytey > 0) {
    float L1 = rot2len(inBytex - offsetX);
    float L2 = rot2len(inBytey - offsetY);

    position = calcPos(L1, L2);

  // Print data on one line, comma-separated, ending with newline
  Serial.print(position.x);
  Serial.print(",");
  Serial.print(position.y);
  Serial.print(",");
  Serial.print(L1);
  Serial.print(",");
  Serial.println(L2);

  delay(50);  // short delay for readability
  }
}
