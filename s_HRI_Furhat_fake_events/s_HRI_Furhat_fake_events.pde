/**
 * Oct 17 / 2025 
 * Faking the state of a Furhat robot, to tell an Arduino over the
 * serial port when the robot is listening '0' or talking '1'
 */

import processing.serial.*;

Serial serial_port;  // Create object from Serial class
String display_message = "";
int[] rgb = new int[3];

void setup() 
{
  size(200, 200);
  String portName = Serial.list()[3];
  rgb[0] = 0;
  rgb[1] = 0;
  rgb[2] = 0;
  
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
  
  println(valueSentToArduino);
  
}

int generateSinValueBasedOnTime()
{
  float   sinValue            = sin(millis() * 0.01);
  float   normalizedValue     = (sinValue + (float)1.0) / (float)2.0;
  float   reMappedToPwnRange  = normalizedValue * 255;// 0 - 255
  int     reMappedSinValue   = (int)reMappedToPwnRange;
  
  return reMappedSinValue;
}

void fakeFurharStates(int reMappedAudioValue){
  
  if (mouseOverRect() == true) {
    rgb[0] = 10;
    rgb[1] = 200;
    rgb[2] = 10;
    display_message = "Furhat Talking";
    serial_port.write(reMappedAudioValue);
  } 
  else {
    rgb[0] = 0;
    rgb[1] = 0;
    rgb[2] = 0;                
    display_message = "Furhat Listening";
    serial_port.write('0');
  }
}

void render(){
  
  background(255);
  fill(rgb[0], rgb[1], rgb[2]);   
  text(display_message, 10, 20);
  rect(50, 50, 100, 100);
  
}

boolean mouseOverRect() {
  
  return ((mouseX >= 50) && (mouseX <= 150) && (mouseY >= 50) && (mouseY <= 150));

}
