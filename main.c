#include <stdio.h>
#include "6190.h"

void quicksort(int *p, int start, int end);

void setup(){
    timerSetup(); 
    setupDisplay();
    eraseBuffer(screen_buffer);
    drawBuffer();
}


void arrayViz(int *arr_to_viz){
    int val, val_for_buf;
    for (int i = 0; i < 8; i += 1){
        val_for_buf = 0;
        val = arr_to_viz[i];
        for (int j = 0; j < val; j+=1){
            val_for_buf |= (1 << j);
        }
        screen_buffer[i] = val_for_buf;
    }
    drawBuffer();
    eraseBuffer(screen_buffer);
    long start = millis();
    while(millis() - start < 100);
}

int testArr[8] = {32, 16, 28, 12, 24, 20, 8, 4};

void app_main() {

    setup();
    srand(60004);

    while(1){
        arrayViz(testArr);
        long start = millis();
        while(millis() - start < 2000);
        quicksort(testArr, 0, 7);
    
        // Restarts automatically        
        testArr[0] = rand() % 32;
        testArr[1] = rand() % 32;
        testArr[2] = rand() % 32;
        testArr[3] = rand() % 32;
        testArr[4] = rand() % 32;
        testArr[5] = rand() % 32;
        testArr[6] = rand() % 32;
        testArr[7] = rand() % 32;

        start = millis();
        while(millis() - start < 2000);
    }
}