//test this out first

void setup() {
  Serial.begin(115200);
  analogReadResolution(12);
}

void loop() {
  int val = analogRead(A0);
  Serial.println(val);
  delayMicroseconds(500);
}