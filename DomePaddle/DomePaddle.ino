 /*
Dome Paddle for MRO using Xbox 360 Controller. Written by Sierra Dodd, Jagdeep Singh and Eva Smerekanych.
  May 2018
Edited by Oliver Fraser and Daniel Orsborn
  November 2020

  Pin Connections on Arduino:
    1) North to pin 2
    2) South to pin 3
    3) East to pin 5
    4) West to pin 4
    5) Dome Left to 14
    6) Dome Right to 16
  
  How to Use:
    1) Connect controller to the arduino using wireless reciever.
    2) Make sure arduino is on
    3) Test controller ouput by holding left trigger on controller and pressing buttons on d-pad,
       lights on controller should change.
    4) Start Bifrost
    5) Turn telescope key
    6) Initialize the telescope
    7) Good to go!
  
  Controls:
    Telescope:
      North: Up
      West:  Right
      East:  Left
      South: Down
    Dome:
      Left:  B
      Right: X
      
    Try to find a way to write a function into the class to distinguish between dome and axis
    Off Button for xbox controller
    If xbox controller disconnects: stop all movement
*/

#include <XBOXRECV.h>
#include <SPI.h>

USB Usb;
XBOXRECV Xbox(&Usb);

// Set your delay time between inputs
class TeleAxis {
//Telescope Axis: Output pins on when low
  public:
  
  TeleAxis(int PositivePin, int NegativePin) {
    _posPin = PositivePin;
    _negPin = NegativePin;
    _state = '0';
    _lastCommandTime = millis();
    pinMode(_posPin, OUTPUT);
    digitalWrite(_posPin, HIGH); //Safegaurd to ensure pins are off during startup
    pinMode(_negPin, OUTPUT);
    digitalWrite(_negPin, HIGH); //Safegaurd to ensure pins are off during startup
  }
  
  boolean MovePositive() {
    if (_state == 'P') {
      // Continues movement in positive direction
      return true;
    } else if (millis() - _lastCommandTime < _teleaxis_delay) {
      // Do not move if it has not been stopped for long enough
      return false;
    } else if (_state == 'N') {
      Stop();
      return false;
    } else if (_state == '0') {
      // We are stopped, so okay to move
      digitalWrite(_posPin, LOW);
      _state = 'P';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; // Return true if it moved positively
    }
    Serial.println("zomg we shouldn't be here in P");
    return false; // Should be impossible to get here
  }
  
  boolean MoveNegative() {
    if (_state == 'N') {
      // Continues movement in negative direction
      return true;
    } else if (millis() - _lastCommandTime < _teleaxis_delay) {
      // Do not move if it has not been stopped for long enough
      return false;
    } else if (_state == 'P') {
      Stop();
      return false;
    } else if (_state == '0') {
      digitalWrite(_negPin, LOW);
      _state = 'N';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; // Return true if it moved negatively
    }
    Serial.println("zomg we shouldn't be here in N");
    return false; // Should be impossible to get here
  }
  
  boolean Stop() {
    if (_state == '0') {
      return true;
    } else if (millis() - _lastCommandTime < _teleaxis_delay) {
      // If any button press happened too close to now, do not stop
      return false;
    } else if (_state != '0') {
      digitalWrite(_posPin, HIGH);
      digitalWrite(_negPin, HIGH);
      _state = '0';
      Serial.println(_state);
      // lastCommandTime set so that it must stay stopped for axis_delay time
      _lastCommandTime = millis();
      return true; // Return true when stopped
    }
    Serial.println("Wowzers thats not stop");
    return false; // Should be impossible to get here
  }
  
    private:
    char _state;
    double _posPin;
    double _negPin;
    unsigned long _lastCommandTime;
    const int _teleaxis_delay = 1000;
};
  
class Axis {
//Dome Axis: Output pins on when high
  public:
  
  Axis(int PositivePin, int NegativePin) {
    _posPin = PositivePin;
    _negPin = NegativePin;
    _state = '0';
    _lastCommandTime = millis();
    pinMode(_posPin, OUTPUT);
    digitalWrite(_posPin, LOW); //Safegaurd to ensure pins are off during startup
    pinMode(_negPin, OUTPUT);
    digitalWrite(_negPin, LOW); //Safegaurd to ensure pins are off during startup
  }
  
  boolean MovePositive() {
    if (_state == 'P') {
      // Continues movement in positive direction
      return true;
    } else if (millis() - _lastCommandTime < _axis_delay) {
      // Do not move if it has not been stopped for long enough
      return false;
    } else if (_state == 'N') {
      Stop();
      return false;
    } else if (_state == '0') {
      // We are stopped, so okay to move
      digitalWrite(_posPin, HIGH);
      _state = 'P';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; // Return true if it moved positively
    }
    Serial.println("zomg we shouldn't be here in P");
    return false; // Should be impossible to get here
  }
  
  boolean MoveNegative() {
    if (_state == 'N') {
      // Continues movement in negative direction
      return true;
    } else if (millis() - _lastCommandTime < _axis_delay) {
      // Do not move if it has not been stopped for long enough
      return false;
    } else if (_state == 'P') {
      Stop();
      return false;
    } else if (_state == '0') {
      digitalWrite(_negPin, HIGH);
      _state = 'N';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; // Return true if it moved negatively
    }
    Serial.println("zomg we shouldn't be here in N");
    return false; // Should be impossible to get here
  }
  
  boolean Stop() {
    if (_state == '0') {
      return true;
    } else if (millis() - _lastCommandTime < _axis_delay) {
      // If any button press happened too close to now, do not stop
      return false;
    } else if (_state != '0') {
      digitalWrite(_posPin, LOW);
      digitalWrite(_negPin, LOW);
      _state = '0';
      Serial.println(_state);
      // lastCommandTime set so that it must stay stopped for axis_delay time
      _lastCommandTime = millis();
      return true; // Return true when stopped
    }
    Serial.println("Wowzers thats not stop");
    return false; // Should be impossible to get here
  }
  
  private:
    char _state;
    double _posPin;
    double _negPin;
    unsigned long _lastCommandTime;
    const int _axis_delay = 1000;
};

//Establish Pins
TeleAxis N_S_Axis(2,3);
TeleAxis E_W_Axis(4,5);
Axis DomeAxis(14,16);
int SetSlewPin = 6; 

void setup() {  
  Serial.begin(9600);
/*#if !defined(__MIPSEL__) //Don't know if we need this step for working with an UNO
  while (!Serial); // Wait for serial port to connect - used on Leonardo, Teensy and other boards with built-in USB CDC serial connection
#endif*/
  if (Usb.Init() == -1) {
    Serial.print(F("\r\nOSC did not start"));
    while (1); //halt
  }
  Serial.print(F("\r\nXBOX USB Library Started"));

  pinMode(SetSlewPin, OUTPUT);

  Serial.println("Paddle Sender is ready!");
}

void loop() {
  
  Usb.Task();
  if (Xbox.XboxReceiverConnected) {
    for (uint8_t i = 0; i < 4; i++){
      if (Xbox.Xbox360Connected[i]) {

        // Speed high and low for telescope movement
        if (Xbox.getButtonClick(START, i)) {
          Xbox.setLedMode(ROTATING, i);
          digitalWrite(SetSlewPin, LOW);
        }

        if (Xbox.getButtonClick(BACK, i)) {
          Xbox.setLedBlink(ALL, i);
          digitalWrite(SetSlewPin, HIGH);
        }
  
        if (Xbox.getButtonPress(L2, i)) {
          if (Xbox.getButtonPress(UP, i) && Xbox.getButtonPress(RIGHT, i)) {
            N_S_Axis.MovePositive();
            E_W_Axis.MovePositive();
            Serial.print("NORTHWEST");
          } else if (Xbox.getButtonPress(DOWN, i) && Xbox.getButtonPress(RIGHT, i)) {
            N_S_Axis.MoveNegative();
            E_W_Axis.MovePositive();
            Serial.print("SOUTHWEST");
          } else if (Xbox.getButtonPress(UP, i) && Xbox.getButtonPress(LEFT, i)) {
            N_S_Axis.MovePositive();
            E_W_Axis.MoveNegative();
            Serial.print("NORTHEAST");
          } else if (Xbox.getButtonPress(DOWN, i) && Xbox.getButtonPress(LEFT, i)) {
            N_S_Axis.MoveNegative();
            E_W_Axis.MoveNegative();
            Serial.print("SOUTHEAST");
          } else if (Xbox.getButtonPress(UP, i)) {  // North
            E_W_Axis.Stop();
            N_S_Axis.MovePositive();
            Serial.print("N");
            break;
          } else if (Xbox.getButtonPress(DOWN, i)) {  // South
            E_W_Axis.Stop();
            N_S_Axis.MoveNegative();
            Serial.print("S");
            break;
          } else if (Xbox.getButtonPress(RIGHT, i)) {  // West
            N_S_Axis.Stop();
            E_W_Axis.MovePositive();
            Serial.print("W");
            break;
          } else if (Xbox.getButtonPress(LEFT, i)) {  // East
            N_S_Axis.Stop();
            E_W_Axis.MoveNegative();
            Serial.print("E");
            break;
          } else {
            N_S_Axis.Stop();
            E_W_Axis.Stop();
          }
        }
// May need to flip directions 
        else if (Xbox.getButtonPress(R2, i)) {
          if (Xbox.getButtonPress(X, i)){ //Dome Left
            DomeAxis.MoveNegative();
            Serial.print("Left");
          }else if (Xbox.getButtonPress(B, i)){ //Dome Right
            DomeAxis.MovePositive();
            Serial.print("Right");
          }else{
             DomeAxis.Stop();
          }
        } else {
          N_S_Axis.Stop();
          E_W_Axis.Stop();
          DomeAxis.Stop();
        }
      }
      /*else{
      N_S_Axis.Stop();
      E_W_Axis.Stop();
      DomeAxis.Stop();
      }*/
    }
  }
}