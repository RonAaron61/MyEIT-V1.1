//https://github.com/MajicDesigns/MD_AD9833/tree/main
//NOT: https://github.com/wollewald/ADS1115_WE/blob/master/examples/Continuous/Continuous.ino
//https://github.com/adafruit/Adafruit_ADS1X15/blob/master/examples/singleended/singleended.ino

#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <MD_AD9833.h>
#include <SPI.h>

Adafruit_ADS1115 ads;

#define Frequency 50000  // Frequency = 50kHz

const uint8_t PIN_DATA = 35;  ///< SPI Data pin number
const uint8_t PIN_CLK = 36;    ///< SPI Clock pin number
const uint8_t PIN_FSYNC = 34; ///< SPI Load pin number (FSYNC in AD9833 usage)
MD_AD9833  AD(PIN_DATA, PIN_CLK, PIN_FSYNC); // Arbitrary SPI pins


int LED1 = 39;
int LED2 = 40;
int LED_BuIn = 15;

float VoltageCall = 0.0;
float Voltage;
int mux[16][4] = {{0,0,0,0}, {0,0,0,1}, {0,0,1,0}, {0,0,1,1}, {0,1,0,0}, {0,1,0,1}, {0,1,1,0}, {0,1,1,1}, {1,0,0,0}, {1,0,0,1}, {1,0,1,0}, {1,0,1,1}, {1,1,0,0}, {1,1,0,1}, {1,1,1,0}, {1,1,1,1}};
float result[208];

byte* ddata = reinterpret_cast<byte*>(&result); // pointer for transferData()
size_t pcDataLen = sizeof(result);

char ser;

#define SDA 8
#define SCL 9
int16_t adc;

void setup(){
  Serial.begin(115200);
  
  //AD9833 object
  AD.begin();
  AD.setFrequency(MD_AD9833::CHAN_0, Frequency);
  AD.setMode(MD_AD9833::MODE_OFF);

  // AD1115
  Wire.begin(SDA, SCL);
  //ads.setGain(GAIN_ONE);  // 1x gain  +/- 4.096V  1 bit = 0.125mV
  ads.setGain(GAIN_TWOTHIRDS);
  if (!ads.begin())
  {
    while (1){
      Serial.println("Failed to initialize ADS.");
    }
  }

  pinMode(1,OUTPUT);
  pinMode(2,OUTPUT);
  pinMode(3,OUTPUT);
  pinMode(4,OUTPUT);

  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,OUTPUT);
  pinMode(10,OUTPUT);

  pinMode(11,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  pinMode(14,OUTPUT);

  pinMode(16,OUTPUT);
  pinMode(17,OUTPUT);
  pinMode(18,OUTPUT);
  pinMode(21,OUTPUT);

  //LED
  pinMode(LED1,OUTPUT);
  pinMode(LED2,OUTPUT);
  pinMode(LED_BuIn,OUTPUT);

  digitalWrite(LED1, HIGH);
  digitalWrite(LED2,1);
  digitalWrite(LED_BuIn, 1);
  delay(1000);
  digitalWrite(LED1, LOW);
  digitalWrite(LED2, 0);
  digitalWrite(LED_BuIn, 0);

}

void Get_Data(int n_elec = 16){
  int a = 0;
  int b = 0;
  //int16_t adc;
  int iter = 0;
  
  AD.setMode(MD_AD9833::MODE_SINE);
  
  digitalWrite(LED1, HIGH);
  for (int i=0; i<n_elec; i++){
    a = i+1;
    if (a >= n_elec){
      a -= n_elec;
    }

    digitalWrite(1,mux[i][0]);
    digitalWrite(2,mux[i][1]);
    digitalWrite(3,mux[i][2]);
    digitalWrite(4,mux[i][3]);

    digitalWrite(5,mux[a][0]);
    digitalWrite(6,mux[a][1]);
    digitalWrite(7,mux[a][2]);
    digitalWrite(10,mux[a][3]);

    for (int j = 0; j<n_elec; j++){
      b = j+1;
      if (b >= n_elec){
        b -= n_elec;
      }

      if ((j == i) || (j == a) || (b ==i)){
        continue;
      }

      //if ((b >= i) && (b <= a+1)){
        //continue;
      //}

      digitalWrite(11,mux[j][0]);
      digitalWrite(12,mux[j][1]);
      digitalWrite(13,mux[j][2]);
      digitalWrite(14,mux[j][3]);

      digitalWrite(16,mux[b][0]);
      digitalWrite(17,mux[b][1]);
      digitalWrite(18,mux[b][2]);
      digitalWrite(21,mux[b][3]);

      //digitalWrite(LED_BuIn, mux[j][3]);

      //delay(2);

      adc = ads.readADC_SingleEnded(0);
      Voltage = ads.computeVolts(adc);
      //result[iter] = ads.computeVolts(adc);
      result[iter] = Voltage + (Voltage*0.1695);
      iter++;
    }
  }
  
  AD.setMode(MD_AD9833::MODE_OFF);
  
  digitalWrite(LED1, LOW);
}


void Tester(int a, int b, int c, int d){
  float adc, v1;
  
  AD.setMode(MD_AD9833::MODE_SINE);
  
  digitalWrite(LED2, HIGH);

  digitalWrite(1,mux[a][0]);
  digitalWrite(2,mux[a][1]);
  digitalWrite(3,mux[a][2]);
  digitalWrite(4,mux[a][3]);

  digitalWrite(5,mux[b][0]);
  digitalWrite(6,mux[b][1]);
  digitalWrite(7,mux[b][2]);
  digitalWrite(10,mux[b][3]);

  digitalWrite(11,mux[c][0]);
  digitalWrite(12,mux[c][1]);
  digitalWrite(13,mux[c][2]);
  digitalWrite(14,mux[c][3]);

  digitalWrite(16,mux[d][0]);
  digitalWrite(17,mux[d][1]);
  digitalWrite(18,mux[d][2]);
  digitalWrite(21,mux[d][3]);


  adc = ads.readADC_SingleEnded(0);
  Voltage = ads.computeVolts(adc);
  v1 = Voltage + (Voltage*0.1695);
  digitalWrite(LED2, LOW);
  Serial.print(Voltage, 5);
  Serial.print(" - ");
  Serial.println(v1, 5);
}


void loop(){

  if(Serial.available() > 0){
    ser = Serial.read();
    if(ser == 'D'){
      Get_Data();
      for (int i=0; i<208;i++){
        Serial.println(result[i],5);
      }
      Serial.println("Done");
    }
    
    else if(ser == 'C'){
      Tester(14,15,12,13);
    }
  }
}
