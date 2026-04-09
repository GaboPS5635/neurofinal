//Here's how this code works (this is assuming we have the neccessary components like a pre amp and a guitar signal coming in):
// 1. It samples the guitar signal at 8kHz assuming the pre amp amp in an acoustic electric guitar holds a 9V battery 
// 2. Removes the DC bias offset introduced by voltage divider circuit
// 3. runs an autocorrelation to find the fundamental frequency of the signal, which is the pitch of the note being played
// 4. Converts the frequence to a note name like E2, A3, etc. 
// 5. PRints it to the Serial Minitor so you can verify it works 

#include <Arduino.h>

#define AUDIO_PIN A0 //places audio pin
#define SAMPLE_RATE 8000 //this is the hz
#define BUFFER_SIZE 512 // samples per buffer
#define MIN_FREQUENCY 60.0f // lowest guitar note is E2 at 82 but we go lower to be safe
#define MAX_FREQUENCY 1400.0f // highest frequency is what we care about i think

//gloabls
int16_t samples[BUFFER_SIZE];
unsigned long sampleInterval;

//naming notes
const char* noteNames[] = {"E2", "F2", "F#2/Gb2", "G2", "G#2/Ab2", "A2", "A#2/Bb2", "B2",
                       "C3", "C#3/Db3", "D3", "D#3/Eb3", "E3", "F3", "F#3/Gb3", "G3",
                       "G#3/Ab3", "A3", "A#3/Bb3", "B3",
                       "C4", "C#4/Db4", "D4", "D#4/Eb4", "E4", "F4", "F#4/Gb4", "G4",
                       "G#4/Ab4", "A4", "A#4/Bb4", "B4",
                       "C5"};

//converts a frequencty to Hz to the nearst note name +octave
 String frequencyToNote(float frequency) {
  if (frequency <= 0) return "---";
  int midiNote = round(12.0 *log2 (frequency / 27.5)+21);
  int octave = (midiNote / 12) - 1;
  int note = midiNote % 12;
  return String(noteNames[note]) + String(octave);
  
}

//returning fundamental frequency in Hz, or 0 if none found
float detectPitch() {
  long sum = 0;
  for (int i = 0; i <BUFFER_SIZE; i++) sum += samples[i];
  int16_t avg = sum / BUFFER_SIZE;
  for (int i = 0; i <BUFFER_SIZE; i++) samples[i] -= avg;

  long bestCorr =0;
  int bestLag =0;
  int minLag = SAMPLE_RATE / MAX_FREQUENCY;
  int maxLag = SAMPLE_RATE / MIN_FREQUENCY;

  // this is sick. this is autocorrelation
  for (int lag = minLag; lag < maxLag && lag < BUFFER_SIZE / 2; lag++) {
    long corr = 0;
    for (int i = 0; i < BUFFER_SIZE / 2; i++) {
      corr += (long)samples[i] * samples[i + lag];
    }
    if (corr > bestCorr) {
      bestCorr = corr;
      bestLag  = lag;
    }
  }

  //silence threshold so if the signal is too weak, it returns to 0 
  if (bestCorr < 1000000L) return 0;
  return (float)SAMPLE_RATE / bestLag;
}

//-------------------––––––––––––

void loop() {
  for (int i = 0; i < BUFFER_SIZE; i++) {
    unsigned long t = micros ();
    samples [i] = (int16_t)analogRead(AUDIO_PIN) - 2048; //center around 0
    while (micros() - t < sampleInterval) { //busy-wait for timing
  }
  float frequency = detectPitch();

  if (frequency > 0) {
    String note = frequencyToNote(frequency);
    Serial.print("Frequency: ");
    Serial.print(frequency, 1);
    Serial.print(" Hz, Note: ");
    Serial.println(note);
  } else {
    Serial.println("No pitch detected");
  }
}

