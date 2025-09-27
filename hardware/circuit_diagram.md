# ESP8266 IDPS Attacker - Circuit Diagram

## Components Required:
- 1x ESP8266 (NodeMCU or Wemos D1 Mini)
- 1x Blue LED (5mm)
- 1x White LED (5mm) 
- 2x 220Ω resistors
- Breadboard and jumper wires

## Circuit Connections:

```
ESP8266 NodeMCU Pin Layout:
                    +---------+
                3V3 |  [ ]    | VIN
                GND |  [ ]    | GND  
                 D0 |  [ ]    | RST
                 D1 |  [ ]    | EN
                 D2 |  [ ]    | 3V3
                 D3 |  [ ]    | GND
                 D4 |  [ ]    | CLK
                3V3 |  [ ]    | SD0
                GND |  [ ]    | CMD
                 D5 |  [●]    | SD1  ← Blue LED (Attack Blocked)
                 D6 |  [●]    | SD2  ← White LED (Attack Success)  
                 D7 |  [ ]    | SD3
                 D8 |  [ ]    | RST
                 RX |  [ ]    | GND
                 TX |  [ ]    | 3V3
                GND |  [ ]    | A0
                3V3 |  [ ]    | RESERVED
                    +---------+
```

## LED Connections:

### Blue LED (Attack Blocked Indicator):
```
ESP8266 D5 ----[220Ω]----[LED+]----[LED-]---- GND
```

### White LED (Attack Success Indicator):
```
ESP8266 D6 ----[220Ω]----[LED+]----[LED-]---- GND
```

## Breadboard Layout:
```
ESP8266 NodeMCU
      |
      |
   +--+--+
   |     |
   D5    D6
   |     |
  [R1]  [R2]  ← 220Ω Resistors
   |     |
 [BLUE] [WHITE] ← LEDs (Anode)
   |     |
   +-----+
      |
     GND ← Common Ground
```

## Power Supply:
- Connect ESP8266 via USB cable to computer for programming and power
- Alternatively, use 3.3V external power supply

## LED Behavior:
- **Blue LED ON**: Attack was blocked by IDPS (HTTP 403)
- **White LED ON**: Attack was successful (HTTP 200) 
- **Both LEDs ON**: Communication error
- **Both LEDs OFF**: Normal idle state or invalid credentials

## Setup Instructions:
1. Connect the circuit as shown above
2. Install ESP8266 libraries in Arduino IDE
3. Update WiFi credentials in the code
4. Update server IP address to match your IDPS system
5. Upload the code to ESP8266
6. Monitor Serial output for attack logs
7. Observe LED indicators for real-time attack status
