#include <pigpio.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define BUZ 4   /*BUZ pin 4, buzzer sound*/
#define AIN1 12 /*BCM pin 12, to spin motor backward*/
#define AIN2 13 /*BCM pin 13, to spin motor forward*/
#define DL 16   /*BCM pin 16, infrared diode*/
#define DR 19   /*BCM pin 19, infrared diode*/
#define BIN1 20 /*BCM pin 20, to spin motor backward*/
#define BIN2 21 /*BCM pin 21, to spin motor forward*/
#define ENA 6   /*BCM pin 6, motor PWM A*/
#define ENB 26  /*BCM pin 26, motor PWM B*/

void report(void) {
  printf("ENA dutycycle %d | %d\n", gpioGetPWMdutycycle(ENA),
         gpioGetPWMrange(ENA));
  printf("ENB dutycycle %d | %d\n", gpioGetPWMdutycycle(ENB),
         gpioGetPWMrange(ENB));
}

void forward() {
  gpioPWM(ENA, 100); /*Set ENA to a low number, maximum is 255*/
  gpioPWM(ENB, 100); /*Set ENB to low number, maximum is 255*/
  gpioWrite(AIN1, 0);
  gpioWrite(AIN2, 1);
  gpioWrite(BIN1, 0);
  gpioWrite(BIN2, 1);
}

void backward(void) {
  gpioWrite(AIN1, 1);
  gpioWrite(AIN2, 0);
  gpioWrite(BIN1, 1);
  gpioWrite(BIN2, 0);
  gpioPWM(ENA, 70);
  gpioPWM(ENB, 70);
}

void stop() {
  gpioWrite(AIN1, 0);
  gpioWrite(AIN2, 0);
  gpioWrite(BIN1, 0);
  gpioWrite(BIN2, 0);
  gpioPWM(ENA, 0);
  gpioPWM(ENB, 0);
}

void beep_on() { gpioWrite(BUZ, 1); }

void beep_off() { gpioWrite(BUZ, 0); }

int main() {
  int init = gpioInitialise();
  if (init < 0) {
    /* pigpio initialisation failed */
    printf("Pigpio initialisation failed. Error code:  %d\n", init);
    exit(init);
  } else {
    /* pigpio initialised okay*/
    printf("Pigpio initialisation OK. Return code:  %d\n", init);
  }

  int mode = PI_OUTPUT;
  
  gpioSetMode(AIN1, mode);
  gpioSetMode(AIN2, mode);
  gpioSetMode(BIN1, mode);
  gpioSetMode(BIN2, mode);
  gpioSetMode(ENA, PI_OUTPUT);
  gpioSetMode(ENB, PI_OUTPUT);
  printf("AIN1 mode %d\n", gpioGetMode(AIN1));
  printf("AIN2 mode %d\n", gpioGetMode(AIN2));
  printf("BIN1 mode %d\n", gpioGetMode(BIN1));
  printf("BIN2 mode %d\n", gpioGetMode(BIN2));
  printf("ENA mode %d\n", gpioGetMode(ENA));
  printf("ENB mode %d\n", gpioGetMode(ENB));
  printf("set PWM ENA %d\n", gpioSetPWMfrequency(ENA, 50000)); /*Set ENA to 50khz*/
  printf("ENA pwm frequency %d\n", gpioGetPWMfrequency(ENA));
  printf("set PWM ENB %d\n", gpioSetPWMfrequency(ENB, 50000)); /*Set ENB to 50khz*/
  printf("ENB pwm frequency %d\n", gpioGetPWMfrequency(ENB));

  stop();

  beep_on();
  sleep(1);
  beep_off();

  forward();
  sleep(3);
  for (int i = 0; i < 2; i++) {
    sleep(1);
    beep_on();
    report();
    sleep(1);
    beep_off();
  }
  backward();

  gpioTerminate();

  return 0;
}
