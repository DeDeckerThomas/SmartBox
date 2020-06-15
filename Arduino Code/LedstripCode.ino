#define DATA_PIN 8
#define NUM_LEDS 120
#define NUM_BYTES (NUM_LEDS*3)
#define PORT PORTB
#define PORT_PIN PORTB0

int VALUES[3] = {0, 0, 0};

String command = "COLOR";
float brightness = 1;
//uint8_t Unsigned integer with a width of 8 bits
uint8_t* memory;

void setup() {
  pinMode(DATA_PIN, OUTPUT);
  memory = (uint8_t*) malloc(NUM_BYTES);  // Allocates the requested memory
  memset(memory, 0, NUM_BYTES);           // Set everything on zero in this block
  Serial.begin(9600);
}

void fill(uint8_t r, uint8_t g, uint8_t b, int delayValue = 30) {
  for (int i = 0; i < NUM_LEDS; i++) {
    setColor(i, r, g, b);
  }
  updateLedstrip();
  delay(delayValue);
}

void checkSerial() {
  if (Serial.available() > 0) {
    String incomingMessage = Serial.readString();
    Serial.println(incomingMessage);
    if (incomingMessage == "STATUS") {
      Serial.println("OK STATUS");
    } else if (incomingMessage == "COLOR") {
      Serial.println("OK COLOR");
      command = "COLOR";
      String data = Serial.readString();
      Serial.println("OK DATA");
      char hex[data.length() + 1];
      data.toCharArray(hex, data.length() + 1);
      char * test = strtok(hex, ";");
      // loop through the string to extract all other tokens
      int index = 0;
      while ( test != NULL ) {
        VALUES[index] = String(test).toInt();
        test = strtok(NULL, ";");
        index++;
      }
    } else if (incomingMessage == "BRIGHTNESS") {
      Serial.println("OK BRIGHTNESS");
      brightness = Serial.readString().toFloat();
    } else if (incomingMessage == "PATTERN") {
      Serial.println("OK PATTERN");
      command = Serial.readString();
    }
  }
}

void wave(uint8_t r, uint8_t g, uint8_t b) {
  for (int i = 0; i < NUM_LEDS; i++) {
    setColor(i, r, g, b);
    updateLedstrip();
    delay(30);
  }

  for (int i = 0; i < NUM_LEDS; i++) {
    setColor(i, 0, 0, 0);
    updateLedstrip();
    delay(30);
  }
}

void rainbow(int delayValue = 100) {
  fill(255, 0, 0, delayValue);
  fill(255, 127, 0, delayValue);
  fill(255, 255, 0, delayValue);
  fill(0, 255, 0, delayValue);
  fill(0, 0, 255, delayValue);
  fill(75, 0, 130, delayValue);
  fill(148, 0, 211, delayValue);
}

void off() {
  memset(memory, 0, NUM_BYTES);
}

// make a color from RGB values, these strips are wired GRB so store in that order
void setColor(uint16_t led, uint8_t r, uint8_t g, uint8_t b) {
  uint8_t *p = memory + led * 3;
  *p++ = g;
  *p++ = r;
  *p = b;
}

void updateLedstrip() {
  noInterrupts(); // Disable interrupts so that timing is as precise as possible
  volatile uint8_t
  *p    = memory,   // Copy the start address of our data array
   val  = *p++,      // Get the current byte value & point to next byte
   high = PORT |  _BV(PORT_PIN), // Bitmask for sending HIGH to pin
   low  = PORT & ~_BV(PORT_PIN), // Bitmask for sending LOW to pin
   tmp  = low,       // Swap variable to adjust duty cycle
   nbits = 8; // Bit counter for inner loop
  volatile uint16_t
  nbytes = NUM_BYTES; // Byte counter for outer loop
  asm volatile(
    // Instruction        CLK     Description                 Phase
    "nextbit:\n\t"         // -    label                       (T =  0)
    "sbi  %0, %1\n\t"     // 2    signal HIGH                 (T =  2)
    "sbrc %4, 7\n\t"      // 1-2  if MSB set                  (T =  ?)
    "mov  %6, %3\n\t"    // 0-1   tmp'll set signal high     (T =  4)
    "dec  %5\n\t"         // 1    decrease bitcount           (T =  5)
    "nop\n\t"             // 1    nop (idle 1 clock cycle)    (T =  6)
    "st   %a2, %6\n\t"    // 2    set PORT to tmp             (T =  8)
    "mov  %6, %7\n\t"     // 1    reset tmp to low (default)  (T =  9)
    "breq nextbyte\n\t"   // 1-2  if bitcount ==0 -> nextbyte (T =  ?)
    "rol  %4\n\t"         // 1    shift MSB leftwards         (T = 11)
    "rjmp .+0\n\t"        // 2    nop nop                     (T = 13)
    "cbi   %0, %1\n\t"    // 2    signal LOW                  (T = 15)
    "rjmp .+0\n\t"        // 2    nop nop                     (T = 17)
    "nop\n\t"             // 1    nop                         (T = 18)
    "rjmp nextbit\n\t"    // 2    bitcount !=0 -> nextbit     (T = 20)
    "nextbyte:\n\t"        // -    label                       -
    "ldi  %5, 8\n\t"      // 1    reset bitcount              (T = 11)
    "ld   %4, %a8+\n\t"   // 2    val = *p++                  (T = 13)
    "cbi   %0, %1\n\t"    // 2    signal LOW                  (T = 15)
    "rjmp .+0\n\t"        // 2    nop nop                     (T = 17)
    "nop\n\t"             // 1    nop                         (T = 18)
    "sbiw %9,1\n\t"       // 1    decrease bytecount          (T = 19)
    "brne nextbit\n\t"    // 2    if bytecount !=0 -> nextbit (T = 20)
    ::
    // Input operands         Operand Id (w/ constraint)
    "I" (_SFR_IO_ADDR(PORT)), // %0
    "I" (PORT_PIN),           // %1
    "e" (&PORT),              // %a2
    "r" (high),               // %3
    "r" (val),                // %4
    "r" (nbits),              // %5
    "r" (tmp),                // %6
    "r" (low),                // %7
    "e" (p),                  // %a8
    "w" (nbytes)              // %9
  );
  delayMicroseconds(50);
  interrupts();
}


void loop() {
  checkSerial();
  if (command == "COLOR") {
    fill(VALUES[0]*brightness, VALUES[1]*brightness, VALUES[2]*brightness, 30);
  } else if (command == "WAVE") {
    wave(0, 0, 255);
  } else if (command == "RAINBOW") {
    rainbow();
  }
}
