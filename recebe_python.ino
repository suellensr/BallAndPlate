#include "Servo.h"                                //biblioteca para o servo
Servo servo1;                                     //cria o objeto servo1
Servo servo2;                                     //cria o objeto servo2
int angulo1=0;                                    //variável para receber o ângulo do servo1
int angulo2=0;                                    //variável para receber o ângulo do servo2

void setup() {
  Serial.begin(9600);                             //inicia a comunicação serial
  servo1.attach(6);                               //anexa o servo 1 ao pino 6
  servo2.attach(9);                               //anexa o servo 2 ao pino 9
  //angulo1 = map(angulo, 80,100,0,126);          //calibração de ângulos do servo 1                                   
  //angulo2 = map(angulo, 80,100,0,160);          //calibração de ângulos do servo 2

}

void loop() {
  while (Serial.available() > 0) {              //enquanto houver dados na comunicação serial, faça...
    

      angulo1 =  Serial.parseInt(); // Lê o número enviado pelo Python
      delay(500);
      angulo2 =  Serial.parseInt(); // Lê o número enviado pelo Python
      delay(500);
      servo1.write(angulo1); //move o servo para o angulo informado
      servo2.write(angulo2); //move o servo para o angulo informado
      
  }
}
