
#include <SPI.h>
#include <Ethernet.h>
#include <OneWire.h>
#include <Wire.h>
#include <BH1750.h>
BH1750 light1;

#include "DHT.h"

#define DHTTYPE DHT11   // DHT 11 
DHT dht(8, DHTTYPE);

OneWire  ds(7);  // on pin 7

byte mac[] = { 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xF1 };
// IP адрес, назначаемый Ethernet shield:
byte ip[] = { 192, 168, 0, 124 };    
//byte ip[] = { 192, 168, 0, 111 };    
// адрес шлюза:
//byte gateway[] = { 192, 168, 0, 1 };
// маска:
//byte subnet[] = { 255, 255, 255, 0 };

EthernetServer server(10001);



byte my_addr[8]={0x28,0x2A,0x78,0x65,5,0,0,0x10};
int count_motion=0;

void setup() {
  Serial.begin(9600);
  Serial.println("start");
  // start the Ethernet connection and the server:
 // инициализация Ethernet shield
  //Ethernet.begin(mac, ip, gateway, subnet);
  Ethernet.begin(mac, ip);
  // запуск сервера
  server.begin();
  Serial.print("server is at ");
  Serial.println(Ethernet.localIP());
  
  Wire.begin();
  delay(1000);
  light1.begin();

  //dps.init(MODE_ULTRA_HIGHRES,69400,true);   
  attachInterrupt(1,motion,RISING);

}


void loop () 
 {
   
  /**/
  EthernetClient client = server.available();
  if (client) {
    // an http request ends with a blank line
    boolean currentLineIsBlank = true;
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        // if you've gotten to the end of the line (received a newline
        // character) and the line is blank, the http request has ended,
        // so you can send a reply
        if (c == '\n' && currentLineIsBlank) {
          // send a standard http response header
          client.println("HTTP/1.1 200 OK");
          client.println("Content-Type: text/html");
          client.println();
          //client.print("Web-server Arduino-Nano-328 <br> ");
          //client.print("DFRduino Ethernet-Shield V 2.0 <br>");
          //client.print("<br>");
          client.print('{');
          client.print('"');client.print("meteo");client.print('"');client.println(":");
          client.print('{');
         
          for (byte thisByte = 0; thisByte < 4; thisByte++) {
             //client.print(Ethernet.localIP()[thisByte], DEC);
             //client.print(".");
             }
          //client.print("<br><br>");
 
          
          //client.print("Показания счетчиков температуры: <br>");
          //client.print("temperatura: <br>");
          
            Serial.print("temp1");
            Serial.print("=");
            int Temp=get_temp();
            Serial.print(Temp/16);
            Serial.print(".");
            Serial.print(((Temp%16)*100)/16);
            Serial.println();
            client.print('"');client.print("temp1");client.print('"');client.print(":");
            client.print('"');client.print(Temp/16);
            client.print(".");
            client.print(((Temp%16)*100)/16);client.print('"');client.print(',');
           float h = dht.readHumidity();
           //float t = dht.readTemperature();
           //Serial.print("humidity4="); 
           //Serial.print(h);
           //Serial.println(" %");
           //Serial.print("temp4="); 
           //Serial.print(t);
           //Serial.println(" *C");
           //client.print('"');client.print("temp4");client.print('"');client.print(":");
           //client.print('"');client.print(t);client.print('"');client.print(',');
           client.print('"');client.print("humidity1");client.print('"');client.print(":");
           client.print('"');client.print(h);client.print('"');
           client.print(',');
           //client.println("}");
           //client.print("}");
           // bh1750
           uint16_t lux = light1.readLightLevel();
           client.print('"');client.print("lux1");client.print('"');client.print(":");
           client.print('"');client.print(lux);client.print('"');
           client.print(',');
          //dps.getTemperature(&Temperature085); 
           uint16_t sound = analogRead(A0);
           client.print('"');client.print("sound1");client.print('"');client.print(":");
           client.print('"');client.print(sound);client.print('"');
           client.print(',');
          //dps.getPressure(&Pressure085);
           //client.print('"');client.print("temp5");client.print('"');client.print(":");
           //client.print('"');client.print(Temperature085*0.1);client.print('"');client.print(',');
           client.print('"');client.print("motion1");client.print('"');client.print(":");
           client.print('"');client.print(count_motion);client.print('"');
           client.println("}");
           client.print("}");
           count_motion=0;
        break;
        }
        if (c == '\n') {
          // you're starting a new line
          currentLineIsBlank = true;
        } 
        else if (c != '\r') {
          // you've gotten a character on the current line
          currentLineIsBlank = false;
        }
      }
    }
    // give the web browser time to receive the data
    delay(1);
    // close the connection:
    client.stop();
  }/**/
 }
// получение тмпературы датчика
int get_temp()
 {
byte i;
byte present = 0;
byte data[12];
byte addr[8];
int Temp;
  /*
  if ( !ds.search(addr)) {
        //Serial.print("No more addresses.\n");
        ds.reset_search();
        return 0;
  }
  Serial.print("R=");  //R=28 Not sure what this is
  for( i = 0; i < 8; i++) {
    Serial.print(addr[i], HEX);
    Serial.print(" ");
  }
  if ( OneWire::crc8( addr, 7) != addr[7]) {
        Serial.print("CRC is not valid!\n");
        return 0;
  }
  if ( addr[0] != 0x28) {
        Serial.print("Device is not a DS18S20 family device.\n");
        return 0;
  }
  */
  ds.reset();
  ds.select(my_addr);
  ds.write(0x44,1);        // start conversion, with parasite power on at the end
  delay(1000);     // maybe 750ms is enough, maybe not
  // we might do a ds.depower() here, but the reset will take care of it.

  present = ds.reset();
  ds.select(my_addr);
  ds.write(0xBE);          // Read Scratchpad
  for ( i = 0; i < 9; i++) {         // we need 9 bytes
    data[i] = ds.read();
  }
  Temp=(data[1]<<8)+data[0];//take the two bytes from the response relating to temperature

  Temp=Temp;//divide by 16 to get pure celcius readout
  
  return Temp;
 }
 
 // обработка прерывания ик датчика движения
//  
void motion()
  {
  //detachInterrupt(0);
  detachInterrupt(1);
  count_motion++;
  Serial.print("motion ");
  Serial.println(millis());
  //delay(2000);
  attachInterrupt(1,motion,RISING);
  }
