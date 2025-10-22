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
  size(200, 200);
  
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
  
  int valueSentToArduino = generateSinValueBasedOnTime();
  fakeFurharStates(valueSentToArduino);
  render();
  
  //println(valueSentToArduino);
  
}

/*
*  Returns a value from [0,255], by remapping a Sin wave over the
*  time since the program started in milliseconds
*/
int generateSinValueBasedOnTime()
{
  float   sinValue            = sin(millis() * 0.005);
  float   normalizedValue     = (sinValue + (float)1.0) / (float)2.0;
  float   reMappedToPwnRange  = normalizedValue * 255;
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
    serial_port.write(val);
    //serial_port.write(reMappedAudioValue);
  } 
  else {
    controlAudioFileBaseOnFurhatState(LISTENING);
    rgb[0] = 0;
    rgb[1] = 0;
    rgb[2] = 0;                
    display_message = "Furhat Listening";
    serial_port.write('A');
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
  
  if(isNormalized)
  {
    audioSample = (audioSample + 1.0) / 2.0;
    audioSample = audioSample > 1.0 ? 1.0 : audioSample;
  }
  
  return   audioSample;
}

void renderVisualFeedbackOfAudioFile()
{
  float val = 100 + (100 * getAudioSample(true));
  
  println(getAudioSample(true));
  noFill();
  noStroke();
  fill(255,0,0);
  ellipse(width/2, height/2, val, val);
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

void render(){
  
  background(255);
  fill(rgb[0], rgb[1], rgb[2]);   
  text(display_message, 10, 20);
  rect(50, 50, 100, 100);
  renderVisualFeedbackOfAudioFile();
  
}

boolean mouseOverRect() {
  
  return ((mouseX >= 50) && (mouseX <= 150) && (mouseY >= 50) && (mouseY <= 150));

}

void keyPressed()
{
  controlAudioFileBaseOnFurhatState(key);
}
