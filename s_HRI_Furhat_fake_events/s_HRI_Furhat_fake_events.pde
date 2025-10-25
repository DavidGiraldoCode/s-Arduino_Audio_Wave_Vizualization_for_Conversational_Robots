/**
 * Oct 17 / 2025 
 * Faking the state of a Furhat robot, to tell an Arduino over the
 * serial port when the robot is listening 'A' or talking [0,255]
 */

import processing.serial.*;
import processing.sound.*;

SoundFile   soundfile;
Serial      serial_port;  // Create object from Serial class
String      display_message   = "";
int[]       rgb               = new int[3];
char        furhatState       = 's';
final char  TALKING           = 't';
final char  LISTENING         = 's';

void setup() 
{
  size(500, 500);
  
  initAudioFile();
  
  String portName = Serial.list()[3];
  rgb[0] = 0;
  rgb[1] = 0;
  rgb[2] = 0;
  
  println("PRINTING AVAILABLE PORTS");
  for(int i = 0; i < Serial.list().length; i++)
  {
    // Prints the list of ports. Check the other IDE what port is the Arduino using.
    println(i + " " + Serial.list()[i]);
  }
  
  serial_port = new Serial(this, portName, 9600);
}

void draw() {
  
  float delta = getAudioSample(false);
  int valueSentToArduino = generateSinValueBasedOnTime();
  fakeFurharStates(valueSentToArduino);
  render(delta);
  
  println(delta);
  
}

/*
*  Returns a value from [0,255], by remapping a Sin wave over the
*  time since the program started in milliseconds
*/
int generateSinValueBasedOnTime()
{
  float   sinValue            = sin(millis() * 0.005);
  float   normalizedValue     = (sinValue + (float)1.0) / (float)2.0;
  //float   reMappedToPwnRange  = normalizedValue * 255;
  float   reMappedToPwnRange  = getAudioSample(true) * 200;
  int     reMappedSinValue    = (int)reMappedToPwnRange;
  
  return reMappedSinValue;
}

/*
* Changes the Fruat state base on a mouse location condition,
* and sends 'A' for listening and the fake sound wave for 
* when it is talking
*/
void fakeFurharStates(int reMappedAudioValue){
  
  if (mouseOverRect() == true) {
    controlAudioFileBaseOnFurhatState(TALKING);
    rgb[0] = 10;
    rgb[1] = 200;
    rgb[2] = 10;
    display_message = "Furhat Talking";
    int val = int(200 * getAudioSample(true));
    //serial_port.write(val);
    //serial_port.write(reMappedAudioValue);
  } 
  else {
    controlAudioFileBaseOnFurhatState(LISTENING);
    rgb[0] = 0;
    rgb[1] = 0;
    rgb[2] = 0;                
    display_message = "Furhat Listening";
    //serial_port.write('A');
  }
}

///////////////////////////////////////////////////////////////
//////////////// AUDIO RELATED ///////////////////////////
///////////////////////////////////////////////////////////////
void initAudioFile()
{
    // load a stereo soundfile with out of phase sine waves in the left and right channel
    soundfile = new SoundFile(this, "npc-arnold-greetings.wav");
  
    println("This sound file of duration " + soundfile.duration() + " seconds" +
      " contains " + soundfile.frames() + " frames, but because it has " + 
      soundfile.channels() + " channels there are actually " + 
      soundfile.channels() * soundfile.frames() +
      " samples that can be accessed using the read() and write() functions");
}

float getAudioSample(boolean isNormalized)
{
  int     frameIndex   = soundfile.positionFrame();
  float   audioSample  = (float) soundfile.read(frameIndex, 0);
  
  if(false)
  {
    audioSample = (audioSample + 2.0) / 2.0;
    audioSample = audioSample > 1.0 ? 1.0 : audioSample;
  }
  
  return   audioSample;
}

float xOffset = 0;
float inverse_cdf_delta = 0;
float expo_delta = 0;
float expo_delta_norm = 0;
float previous_delt = 0;
float log_n = 0;
// Only one channel is consider in this code.
// The normalization is using magic number, fine tunning.

// Global variables for dynamic normalization (Peak Tracking)
float currentPeak = 0.001; // Initialize to a small non-zero value
final float PEAK_DECAY_RATE = 0.98; // How fast the peak drops (e.g., 0.98 per frame/update)
final float PEAK_GROWTH_RATE = 0.05; // How fast the peak rises

void renderVisualFeedbackOfAudioFile(float delta)
{
  //float val = 100 + (100 * delta);
  xOffset+=0.05;
  
  noFill();
  
  
  
  delta = delta * delta;
  delta = sqrt(delta);
  
  // Slowly decay the current tracked peak (slow drop)
  currentPeak *= PEAK_DECAY_RATE;
  float instantaneous_amplitude = delta;
  if(instantaneous_amplitude > currentPeak)
  {
    // Review this math
    //currentPeak += (instantaneous_amplitude - currentPeak) * PEAK_GROWTH_RATE;
    currentPeak = instantaneous_amplitude;
  }
  
  // Ensure the peak doesn't fall to zero (avoid division by zero)
  if (currentPeak < 0.001) currentPeak = 0.001;
  
  // 3. Normalize the data against the dynamically tracked peak
  // The normalized value is now guaranteed to be between [0.0, 1.0]
  float delta_norm = instantaneous_amplitude / currentPeak;
  
  delta = delta > 3 ? 1 : delta/3;
  
  expo_delta = 1 - exp(-10 * delta);
  expo_delta_norm = 1 - exp(-10 * delta_norm);
  
  fill(255,0,0);
  int left_margin = 40;
  fill(0);
  rect(width - (left_margin+10), 0 , width , height);
  for(int i = 0; i <= 10; i++)
  {
    fill(150);
    text(((float)i/10.0), width - left_margin, (height/2) - 200*((float)i/10.0));
    stroke(150);
    line(0, (height/2) - 200*((float)i/10.0) , width, (height/2) - 200*((float)i/10.0) );
  }
  stroke(0);
  line(0, (height/2) , width, (height/2));
  noStroke();
  
  fill(0,255,0);
  //ellipse(left_margin + xOffset, (height/2) - (delta * 200), 2, 2);
  
  fill(255,255,0);
  ellipse(left_margin + xOffset, (height/2) - (delta_norm * 200), 2, 2);
  
  fill(0,0,255);
  //ellipse(left_margin + xOffset+4, (height/2) - (expo_delta * 200), 2, 2);
  
  fill(0,255,255);
  ellipse(left_margin + xOffset+4, (height/2) - (expo_delta_norm * 200), 2, 2);
  
  fill(0);
  rect(0,height/2,width,height);
  
  fill(255,0,0);
  //(1 - t) f(0) + t  f(1)
  float t = 0.5;
  float interpolated_delta = 0.0;
  interpolated_delta = (1-t)*interpolated_delta + t*expo_delta_norm;
  float base = 50.0;
  float growth = 50.0;
  float original_growth = base + (growth * delta_norm);
  float expo_growth = base + (growth * expo_delta_norm);
  ellipse((width/3), (3*height/4), original_growth, original_growth);
  ellipse((2*width/3), (3*height/4), expo_growth, expo_growth);

  previous_delt = expo_delta_norm;
}

void controlAudioFileBaseOnFurhatState(char furhatState)
{
  switch(furhatState)
  {
    case 't': // Talking
      if(!soundfile.isPlaying())
        soundfile.play();
    break;
    case 'p': // pause
      if(soundfile.isPlaying())
        soundfile.pause();
    break;
    case 's': // stop
      if(soundfile.isPlaying())
      {
        soundfile.pause();
        soundfile.jump(0.0);
        soundfile.pause();
      }
    break;
  }
}
///////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////

void render(float delta){
  
  //background(0, 0.1);
  renderVisualFeedbackOfAudioFile(delta);
  fill(rgb[0], rgb[1], rgb[2]);   
  //text(display_message, 10, 20);
  rect(20, (height/2) + 10, 40, 40);
  
  
}

boolean mouseOverRect() {
  
  return ((mouseX >= 20) && (mouseX <= 60) && (mouseY >= (height/2) + 10) && (mouseY <= (height/2) + 50));

}

void keyPressed()
{
  controlAudioFileBaseOnFurhatState(key);
}
/*
delta = delta * delta;
  delta = sqrt(delta);
  delta = delta > 3 ? 1 : delta/3;
  //expo_delta = 1 - exp(-1.5*delta);
  inverse_cdf_delta = (-1/1.5)*log(1-delta);
  expo_delta = 1 - exp(-10 * delta);
  //expo_delta = expo_delta > 1? 1 : expo_delta;
  log_n = 1.0 + log(delta);
  //log_n = sqrt(log_n*log_n);
  log_n = log_n > 1 ? 1 : log_n;
  //1 − e − λx
  println(delta);
  
  fill(255,0,0);
  //ellipse(width/2, height/2, val, val);
  
  //line(width/3, (height - 20) , width/3, (height - 420));
*/
