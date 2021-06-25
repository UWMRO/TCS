 /*
  The Dome Paddle controls the telescope and dome based on inputs from an Xbox controller, 
  but ensuring smooth motions. This sketch is used to test the logic using wired buttons for 
  input, leds for output. 

  The motion of each axis is controlled by implimenting an 'axis' object which: 
  - ensures moves move for a minimum time
  - ensures stops last for a minimum time too
  - forces a pass through stop before reversing

  Originally written by Sierra Dodd, Jagdeep Singh and Eva Smerekanych May 2018
  Restructured by Daniel Orsborn and Oliver Fraser
*/

const int NorthPin = 9;
const int SouthPin = 10;
const int EastPin = 11;
const int WestPin = 12;

class Axis {
/*
  Axis keeps track of it's state (_state): 
  - stopped (0), 
  - moving in the positive direction (P), 
  - or the negative (N)
*/
  public:
  
  Axis(int PositivePin, int NegativePin) {
    _posPin = PositivePin;
    _negPin = NegativePin;
    _lastCommandTime = 0;
    pinMode(_posPin, OUTPUT);
    pinMode(_negPin, OUTPUT);
    Stop();
  }
  
  boolean MovePositive() {
    if (_state == 'P') {
      return true;
    }
    else if (millis() - _lastCommandTime < 1000) {
      return false;
    }
    else if (_state == 'N') {
      Stop();
      return false;
    }
    else if (_state == '0') {
      // we are stopped, so okay to move
      digitalWrite(_posPin, LOW);
      _state = 'P';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; //return true if it moved positively
    }
    Serial.println("zomg we shouldn't be here in P");
    return false; // should be impossible to get here
  }
  
  boolean MoveNegative() {
    if (_state == 'N') {
      return true;
    }
    else if (millis() - _lastCommandTime < 1000) {
      return false;
    }
    else if (_state == 'P') {
      Stop();
      return false;
    }
    else if (_state == '0') {
      digitalWrite(_negPin, LOW);
      _state = 'N';
      _lastCommandTime = millis();
      Serial.println(_state);
      return true; //return true if it moved negatively
    }
    Serial.println("zomg we shouldn't be here in N");
    return false; // should be impossible to get here
  }
  
  boolean Stop() {
    if (_state == '0') {
      return true;
    }
    else if (millis() - _lastCommandTime < 1000) {
      return false;
    }
    else if (_state != '0') {
      digitalWrite(_posPin, HIGH);
      digitalWrite(_negPin, HIGH);
      _state = '0';
      Serial.println(_state);
      _lastCommandTime = millis();
      return true; //return true if it stopped
    }
    Serial.println("zomg we shouldn't be here in stop");
    return false; // should be impossible to get here
  }
  
  private:
    char _state;
    double _posPin;
    double _negPin;
    unsigned long _lastCommandTime;
};

//Axis N_S_Axis(2,3);
Axis E_W_Axis(4,5);

void setup() {  
  // make the pushbutton's pin an input:
  pinMode(NorthPin, INPUT_PULLUP);//North
  pinMode(SouthPin, INPUT_PULLUP);//South
  pinMode(EastPin, INPUT_PULLUP);//East
  pinMode(WestPin, INPUT_PULLUP);//West
  Serial.begin(9600);
  Serial.println("Paddle Sender is ready!");
}

void loop() {
  
/*  if (digitalRead(NorthPin)==0) {
    N_S_Axis.MovePositive();
  }
  else if (digitalRead(SouthPin)==0) {
    N_S_Axis.MoveNegative();
  }
  else { 
    N_S_Axis.Stop();
  }
*/
  if (digitalRead(EastPin)==0) {
    E_W_Axis.MovePositive();
  }
  else if (digitalRead(WestPin)==0) {
    E_W_Axis.MoveNegative();
  }
  else { 
    E_W_Axis.Stop();
  }
}