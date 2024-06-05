#include <stdio.h>
#include <stdint.h>

/* Header File for 6.190, using the ESP32-C3 */
/* ESP32-C3 Reference: https://www.espressif.com/sites/default/files/documentation/esp32-c3_technical_reference_manual_en.pdf */

///////////////////////////////
// Peripheral Base Addresses //
///////////////////////////////

// Functions implemented in assembly must be declared in C.
void pinWrite(int pin_num, int value);
int pinRead(int pin_num);
void pinSetup(int pin_num, int mode);
void setPixel(uint32_t *screen_buffer_addr, uint8_t x, uint8_t y, uint8_t val);
void eraseBuffer(uint32_t *screen_buffer_addr);


#define GPIO_BASE_ADDR                      0x60004000  // Base address for memory locations dedicated to GPIO matrix 
#define IO_MUX_BASE_ADDR                    0x60009000  // Base address for memory locations dedicated to IO multiplexer addresses
#define TIMER_BASE_ADDR                     0x6001F000  // Base address for memory locations dedicated to timer 


///////////////////////////////////////////////
// General-Purposed Input/Output Definitions //
///////////////////////////////////////////////

/* GPIO Addresses */
#define GPIO_OUT_ADDR                       (GPIO_BASE_ADDR + 0x0004)
#define GPIO_ENABLE_ADDR                    (GPIO_BASE_ADDR + 0x0020)
#define GPIO_IN_ADDR                        (GPIO_BASE_ADDR + 0x003C)
#define IO_MUX_GPIOn_ADDR                   (IO_MUX_BASE_ADDR + 0x0004) // 1 memory location/pin, need to add 4n for pin n

/* GPIO Pin Modes */
#define GPIO_INPUT 0
#define GPIO_OUTPUT 1

/* GPIO -> Peripheral Mapping */

// Switches
#define SW7 9
#define SW6 8
#define SW5 7
#define SW4 6
#define SW3 5
#define SW2 4
#define SW1 18
#define SW0 19

// Buttons
#define BTNF 9
#define BTNU 8
#define BTNC 7
#define BTND 6
#define BTNR 5
#define BTNL 4

// LEDs
#define LED1 2
#define LED2 3


// /* GPIO Functions */
// void pinSetup(int pin_num, int mode){
//     /* Setup function to configure GPIO pin (pin_num) as either an input
//     or an output, as defined by mode.

//     Arguments:
//         pin_num: GPIO pin number (0 - 31)
//         mode: Mode to configure pin as. GPIO_INPUT = 0, GPIO_OUTPUT = 1
//     */

//     if (mode == GPIO_INPUT){
//         // Configure GPIO pin pin_num as input
//         int *io_mux_gpio_addr = (int*) (IO_MUX_GPIOn_ADDR + (4*pin_num));
//         *io_mux_gpio_addr |= (1 << 8); //for each bit, move 1
//         *io_mux_gpio_addr |= (1 << 9); 
        
//     } else if (mode == GPIO_OUTPUT){
//         // Configure GPIO pin pin_num as output.
//         int *gpio_enable_addr = (int*) GPIO_ENABLE_ADDR;
//         *gpio_enable_addr |= (1 << pin_num); //just for n given by pin_num
//     }

// }






// void pinWrite(int pin_num, int value){
//     /* Function to write either 0 or 1 (value) to an output GPIO pin (pin_num)
//     Arguments:
//         pin_num: GPIO pin number (0 - 31)
//         value: digital value (0 or 1) to write to GPIO pin
//     */

//     int *output_val = (int*) GPIO_OUT_ADDR;
//     if (value != 0) value = 1; // set non-zero inputs to 1 (HIGH)
//     *output_val &= ~(1 << pin_num); //clear bits at pin

//     *output_val |= (value << pin_num); //set new value using pointer
// }


// int pinRead(int pin_num){
//     /* Function to read the value of an input GPIO pin (pin_num). 
//     Arguments: 
//         pin_num: GPIO pin number (0 - 31)
//     Returns: 
//         int: digital value (0 or 1) read from GPIO pin
//     */

//    int* input_val = (int*) GPIO_IN_ADDR;

//     int bit = (*input_val >> pin_num) & 1; //read value using bitwise op

//    return bit; // replace 0 with return value of pinRead
   
// }

///////////////////////
// Timer Definitions //
///////////////////////

/* Timer Addresses */
#define TIMER_CONFIG_ADDR               (TIMER_BASE_ADDR + 0x0000)
#define TIMER_COUNT_LO_ADDR             (TIMER_BASE_ADDR + 0x0004)
#define TIMER_COUNT_HI_ADDR             (TIMER_BASE_ADDR + 0x0008)
#define TIMER_COUNT_UPDATE_ADDR         (TIMER_BASE_ADDR + 0x000C)

#define WATCHDOG_CONFIG_ADDR            (TIMER_BASE_ADDR + 0x0048)
#define WATCHDOG_WRITE_PROTECT_ADDR     (TIMER_BASE_ADDR + 0x0064)

/* Timer Functions */
void timerSetup(void){
    /* Setup function to initalize Timer 0 in the ESP32-C3 Timer Group. */

    // Configure timer by choosing clock source (external clock),  prescalar value (0x01) and direction (increment). 
    int* timg_t0_config = (int*) TIMER_CONFIG_ADDR;
    *timg_t0_config = (*timg_t0_config) | (0x01 << 9) | (0x01 << 13) | (0x01 << 30);

    // Start timer by setting most sigificant bit (MSB) of value at timer configuration memory address 
    *timg_t0_config |= (0x01 << 31);

    // Turn off watchdog timer timeout messages 
    int* wdog_addr = (int*) WATCHDOG_WRITE_PROTECT_ADDR;
    *wdog_addr = 0x50d83aa1;

    int* wdog_cfg = (int*) WATCHDOG_CONFIG_ADDR;
    *wdog_cfg &= ~(0x01 << 31); // clear bit 31
}


uint64_t millis(void){
    /* Converts the value of the counter driven by a 40MHz clock
    to a time-stamp in milliseconds.*/
    
    // write to MSB of value at timer counter update address to latch (update/retain) value of counter
    int* timg_to_update = (int*) TIMER_COUNT_UPDATE_ADDR;
    *timg_to_update |= (1 << 31);
   
    // (2) actually read... 
    int* timer_lo = (int*) TIMER_COUNT_LO_ADDR; // read low 32 bits of counter value
    int* timer_hi = (int*) TIMER_COUNT_HI_ADDR; // upper 22 bits of counter value
    uint32_t timer_lo_val = (uint32_t) *timer_lo;
    uint32_t timer_hi_val = (uint32_t) *timer_hi;
    uint64_t bigger_timer_hi = (uint64_t) timer_hi_val;

    return ((bigger_timer_hi << 32) + timer_lo_val) >> 14;
}


uint64_t micros(void){
    /* Converts the value of the counter driven by a 40MHz clock
    to a time-stamp in microseconds.*/
    
    // write to MSB of value at timer counter update address to latch (update/retain) value of counter
    int* timg_to_update = (int*) TIMER_COUNT_UPDATE_ADDR;
    *timg_to_update |= (1 << 31);
   
    int* timer_lo = (int*) TIMER_COUNT_LO_ADDR; // read low 32 bits of counter value
    int* timer_hi = (int*) TIMER_COUNT_HI_ADDR; // upper 22 bits of counter value
    uint32_t timer_lo_val = (uint32_t) *timer_lo;
    uint32_t timer_hi_val = (uint32_t) *timer_hi;
    uint64_t bigger_timer_hi = (uint64_t) timer_hi_val;

    return ((bigger_timer_hi << 32) + timer_lo_val) >> 4;
}

/////////////////////////////////////////////////
// Serial Peripheral Interface (SPI) Functions //
/////////////////////////////////////////////////

/* Mapping of GPIO pin to SPI signal */
#define CLK 0
#define CS 1
#define MOSI 10

void spiPause(){
    /* 1 microsecond delay for SPI timing */

    uint64_t t = micros();
    while(micros()-t<1);
}


void spiWrite(uint8_t *data, uint8_t len, uint8_t clk_pin, uint8_t mosi_pin, uint8_t cs_pin ){
    /* Performs software-driven SPI write
     Arguments:
        data: pointer to array of 8-bit values to be sent serially
        len: number of 8-bit values to write
        clk_pin: GPIO pin used to generate clock signal
        mosi_pin: GPIO pin used to transmit data serially
        cs_pin: GPIO pin used for chip select
    */

    pinWrite(cs_pin,0); // bring chip select signal low

    // Send data in buffer in 8-bit chunks
    // Generate clock signal and send 1 bit/clock period
    for (int q=0; q<len; q++){
        for (int p=0; p<8; p++){
            pinWrite(clk_pin,0);
            pinWrite(mosi_pin,((data[q]>>p)&0x01));
            spiPause();
            pinWrite(clk_pin,1);
            spiPause();
        }
    }
    pinWrite(cs_pin,1); // bring chip-select signal high
}

/////////////////
// LED Display //
/////////////////

// LED Display Driver (MAX7219) Documentation: https://datasheets.maximintegrated.com/en/ds/MAX7219-MAX7221.pdf

/* Helper functions for flipping bits */
void bit_reverse(int value, int *dump){
    for (int i = 0; i<32; i++){
        *dump = ((*dump)<<1)|((value>>i)&0x1);
    }
}

uint8_t flip_8(uint8_t value){
    uint8_t t =0;
    for (int i = 0; i<8; i++){
        t = (t<<1)|((value>>i)&0x1);
    }
    return t;
}

/* LED Display Driver Functions */
void setupDisplay(){
    /* Function to set up LED display */

    // Set up necessary GPIO pins
    pinSetup(CS, GPIO_OUTPUT);
    pinSetup(MOSI, GPIO_OUTPUT);
    pinSetup(CLK, GPIO_OUTPUT);

    // Pull chip select, clock, and data out high
    pinWrite(CS,1);
    pinWrite(MOSI,1);
    pinWrite(CLK,1);

    // Configure LED display
    int DISP_TEST = 0x0F000F00; //display test
    int DISP_OFF = 0x0C000C00;  //display off
    int DISP_ON = 0x0C010C01;   //display on
    int DEC_0 = 0x09000900;     //decode mode 0
    int SCAN_M = 0x0B070B07;    //scan mode setting
    int INTENSITY = 0x0A010A01; //screen intensity

    int config_buffers[] = {DISP_TEST, DISP_OFF, DISP_ON, DEC_0, SCAN_M, INTENSITY};

    for (int i = 0; i < 6; i = i + 1){
        int t[2] = {0,0};
        bit_reverse(config_buffers[i],t);
        bit_reverse(config_buffers[i],t+1);
        uint8_t *s = (uint8_t*)t;
        for (int i = 0; i<4; i++){
            spiWrite(s,2,CLK,MOSI,CS);
        }

        int del = millis();
        while(millis()-del<5);
    }
}

uint32_t screen_buffer [8]; // 8x32 array for storing LED display image

// void eraseBuffer(){
//     /* Function that clears screen buffer by setting all bits to 0. */

//     for (uint8_t i=0; i<8; i++){
//         screen_buffer[i]=0;     //set all 32 bits to 0
//     }
// }

void drawBuffer(){
    /* Function that sends bytes in screen buffer to be displayed on LED array.*/

    uint8_t buffer[8];
    for (int k = 1; k <9; k++){
        for (int m=0; m<4;m++){
            buffer[0+2*m] = (uint8_t)flip_8(9-k);
            uint8_t temp = (uint8_t)(screen_buffer[k-1]>>(8*m));
            buffer[1+2*m] = temp & 0x000000FF;
        }
        spiWrite(buffer,8,CLK,MOSI,CS);
    }
}