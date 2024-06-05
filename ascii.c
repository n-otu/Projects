#include <stdio.h>
#include "6190.h"

void setup(){

    timerSetup();   // Configure timer
    setupDisplay(); // Configure display
    eraseBuffer();  // Erase random data from display
    drawBuffer();   // Display contents of buffer on LED array
}


int messageLength(char* message){

    //////////////////////////////////////////
    // TO-DO: Complete messageLength()      //
    //////////////////////////////////////////

    int count = 0;
    for (int i = 0; i <=100000000000; i++) {//arbitrary number
        if (message[i] != '\0') {
            count = count + 1; //update count, continue
        }
        else {
            return count;
        }
    }
}


void fillScreenBuffer(char* message, int total_offset){

    //////////////////////////////////////////
    // TO-DO: Complete fillScreenBuffer()   //
    //////////////////////////////////////////

    int val = total_offset/8; //first letter index to display
    int shift_imp = (total_offset % 8); //from 2nd eq above
    
    ///start of code similar to drawAscii
    eraseBuffer(); ///clear at tart 
    int x = val;
    while (x <= val + 3) { ///iterate 3 letters after val index
        int y = 0;
        int asc = message[x]; //ascii val of letter
        int shift = (3 - (x-val)) * 8 + shift_imp; //amount to shift each letter by
        for (int i = 0; i <= 7; i++) {
            if (asc == 0) {//null found early
                y = 1;
                break;}
            else { //proceed as normal
                screen_buffer[i] |= (ascii[asc][i] << shift);}
 
        } //end of 2nd for loop  
        x = x + 1;
        if (y == 1) {break;}
        }
    if (x > val + 3) {
        int y = 0;
        int asc = message[x]; //ascii val of letter
            int new_shift = 8 - shift_imp;
            for (int i = 0; i <= 7; i++) {
                if (asc == 0) {//null found early

        y = 1;
                    break;}
                else { //proceed as normal
                    screen_buffer[i] |= (ascii[asc][i] >> new_shift);}
                if (y == 1) {break;}
            }
    
        
        }//end of 1st while loop
     
    drawBuffer(); //now add info to buffer
}   


void app_main(){
    setup();
    
    char message[] = "     THEY SEE ME SCROLLIN' THEY HATIN'     ";
    // char message[] = " GOJO IS MY GLORIOUS BLUE-EYED KING <3 ";
    int len = messageLength(message);  // TASK 1: CALCULATE MESSAGE LENGTH
    int offset = 0;
    while(1){
        if (offset == len * 8){  
            offset = 0; // Reset if we have reached the end of the message
        } else {
            eraseBuffer();  // Clear screen buffer
            fillScreenBuffer(message, offset); // TASK 2: FILL SCREEN BUFFER WITH CORRECT DATA
            drawBuffer();   // Transmit screen buffer data to screen
            offset++;        // Move forward
        }

        int start = millis();            // Get "start" time stamp
        while(millis() - start < 100);   // Wait until (current time stamp - "start") >= 100ms   
    }
}
