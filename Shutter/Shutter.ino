#include <FlexiTimer2.h>
#include "Shutter.h"

/* hl lib : HIGH/LOW at tick interval */

#define hl_declare(N) uint8_t hl_buffer[N];
extern	uint8_t hl_buffer[];
volatile uint8_t hl_count;
volatile uint8_t hl_stop;
volatile uint8_t hl_wait;
volatile uint8_t hl_index;

void hl_init() {
	hl_count = 0;
	hl_index = 0;
	hl_stop = 0;
	hl_wait = 0;
}

void hl_push_high(uint8_t duration) {
	hl_buffer[hl_count] = duration << 1 | 1;
	hl_count++;
}
void hl_push_low(uint8_t duration) {
	hl_buffer[hl_count] = duration << 1 | 0;
	hl_count++;
}

/* shutter lib : private */

void hl_push_shutter_preemble() {
	hl_push_low(50);
	hl_push_high(50);
	hl_push_low(6);
}

void hl_push_shutter_0() {
	hl_push_high(6);
	hl_push_low(2);
}

void hl_push_shutter_1() {
  hl_push_high(2);
	hl_push_low(6);
}

void hl_push_shutter_end() {
	hl_push_high(4);
	hl_push_low(4);
	hl_push_high(40);
	hl_push_low(1);
}

void hl_push_shutter_code(const char *str) {
	int i = 0;
	while(str[i]) {
		switch (str[i]) {
			case '0': hl_push_shutter_0(); break;
			case '1': hl_push_shutter_1(); break;
		};
		i++;
	}
}

/* shutter lib public */

void shutter_init() {
	FlexiTimer2::set(1, 1.0/10000, tick);
}

void shutter_send_code(const char *str) {
	hl_init();
	hl_push_shutter_preemble();
	hl_push_shutter_code(str);
	hl_push_shutter_end();	
	FlexiTimer2::start();
	while(!hl_stop)
		;
	FlexiTimer2::stop();
}

void shutter_send_up() {
	Serial.println("send up");
	shutter_send_code(SHUTTER_UP);
}

void shutter_send_down() {
	Serial.println("send down");
	shutter_send_code(SHUTTER_DOWN);
}

void shutter_send_stop() {
	Serial.println("send stop");
	shutter_send_code(SHUTTER_STOP);
}

/* le code */

void tick(void) {
	if (--hl_wait) 
		return;
	if (hl_index == hl_count) {
		hl_stop = 1;
		return;
	}
	uint8_t instr = hl_buffer[hl_index++];
	digitalWrite(12, instr & 1 ? HIGH : LOW);
	hl_wait = instr >> 1;	
}

hl_declare(300);

void setup() {
	Serial.begin(9600);
	Serial.println("ready");
	shutter_init();
	delay(500);
	shutter_send_up();
	delay(500);
	shutter_send_stop();
	delay(2000);
	shutter_send_down();
}

void loop() {
}
