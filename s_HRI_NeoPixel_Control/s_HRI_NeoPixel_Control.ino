#include <Adafruit_NeoPixel.h>

#define LED_PIN     6          // Data pin for the NeoPixel ring
#define NUM_PIXELS  16         // Number of LEDs in the ring

Adafruit_NeoPixel ring(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);
uint8_t brightness;
void setup()
{
  Serial.begin(9600);
  ring.begin();
  ring.show();
}

void loop()
{
 	brightness = 128 ;

  ring.setBrightness(brightness);

  for (int i = 0; i < NUM_PIXELS; i++)
  {
    ring.setPixelColor(i, ring.Color(250, 200, 200));
  }
  ring.show();

  delay(250);
  
  brightness = 250 ;
  ring.setBrightness(brightness);

  for (int i = 0; i < NUM_PIXELS; i++)
  {
    ring.setPixelColor(i, ring.Color(250, 200, 200));
  }
  ring.show();
  
  delay(250);
}
