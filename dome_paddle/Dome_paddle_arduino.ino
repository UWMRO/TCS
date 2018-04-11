/*
 Example sketch for the Xbox 360 USB library - developed by Kristian Lauszus
 For more information visit my blog: http://blog.tkjelectronics.dk/ or
 send me an e-mail:  kristianl@tkjelectronics.com
 */

#include <XBOXRECV.h>
#include <SoftwareSerial.h>

// Satisfy the IDE, which needs to see the include statment in the ino too.
#ifdef dobogusinclude
#include <spi4teensy3.h>
#endif
#include <SPI.h>

USB Usb;
XBOXRECV Xbox(&Usb);

Axis N_S_Axis(8,9);
Axis E_W_Axis(10,11);

void setup() {
  Serial.begin(115200);
#if !defined(__MIPSEL__)
  while (!Serial); // Wait for serial port to connect - used on Leonardo, Teensy and other boards with built-in USB CDC serial connection
#endif
  if (Usb.Init() == -1) {
    Serial.print(F("\r\nOSC did not start"));
    while (1); //halt
  }
  Serial.print(F("\r\nXBOX USB Library Started"));
}
void loop() {
  Usb.Task();
  if (Xbox.XboxReceiverConnected) {
    for (uint8_t i = 0; i < 4; i++){
      if (Xbox.Xbox360Connected[i]) {
        if (Xbox.getButtonClick(UP, i)) {  // North
          Xbox.setLedOn(LED1);
          N_S_Axis.MovePositive();
          break;
        } else if (Xbox.getButtonClick(DOWN, i)) {  // South
          Xbox.setLedOn(LED4);
          N_S_Axis.MoveNegative();
          break;
        } else if (Xbox.getButtonClick(LEFT, i)) {  // West
          Xbox.setLedOn(LED3);
          E_W_Axis.MovePositive();
          break;
        } else if (Xbox.getButtonClick(RIGHT, i)) {  // East
          Xbox.setLedOn(LED2);
          E_W_Axis.MoveNegative();
          break;
        } else {
          N_S_Axis.Stop();
          E_W_Axis.Stop();
        }
      }
    }
  delay(1);
  }
}

class Axis {
  public:
  
  Axis(int PositivePin, int NegativePin) {
    _posPin = PositivePin;
    _negPin = NegativePin;
    _lastCommandTime = 0;
    pinMode(_posPin, OUTPUT);
    pinMode(_negPin, OUTPUT);
    _state = 0;
  }
  
  void MovePositive() {
    if (_state != 'N') {
      digitalWrite(_posPin, HIGH);
      _state = 'P';
      _lastCommandTime = millis();
      Serial.print('P');
    }
  }

  void MoveNegative() {
    if (_state != 'P') {
      digitalWrite(_negPin, HIGH);
      _state = 'N';
      _lastCommandTime = millis();
      Serial.print('N');
    }
  }
  
  void Stop() {
    if (millis() - _lastCommandTime > 200) {
      digitalWrite(_posPin, LOW);
      digitalWrite(_negPin, LOW);
      _state = 0;  
    }
    else {
      Serial.print("Too soon ");
    }
  }

  private:
    char _state;
    double _posPin;
    double _negPin;
    unsigned long _lastCommandTime;
};
