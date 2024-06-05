#include <stdio.h>
#include <stdint.h>
#include "6190.h"

// Constants
#define SCREEN_ROWS 8
#define SCREEN_COLS 32
enum snake_direction { up, down, left, right };

// Setup for random value generator
#define RANDOM_VALUE_ADDR 0x600260B0 
#define RTC_CNTL_CLK_CONF_REG 0x60008070

void setupRandom(){
    int *rtc_cntl_clk_conf_rg = (int*) RTC_CNTL_CLK_CONF_REG;
    *rtc_cntl_clk_conf_rg |= (1 << 10);
}


// Snake struct definition
struct Snake {
    uint8_t body[SCREEN_COLS*SCREEN_ROWS]; // can get as large as entire screen in theory
    uint8_t direction;
    uint8_t length; 
};


void setup(){
    timerSetup();
    setupRandom();
    setupDisplay();
    eraseBuffer();
    int snake_buttons[5] = {BTNF, BTNU, BTND, BTNR, BTNL};
    for (int i = 0; i < 5; i++){
        pinSetup(snake_buttons[i], GPIO_INPUT);
    }
}


uint8_t getX(uint8_t location){
    /* Function that returns the x coordinate from an 8-bit value containing both x and y coordinates.
        The x coordinate is encoded in the upper (most significant) 5 bits of the input.
    Arguments: 
        location: an unsigned 8-bit value representing a location on an 8x32 gameboard.
    Returns: 
        uint8_t representing the x-coordinate (0-31) encoded in the upper 5 bits of the argument.
    */

    //////////////////////////////
    // TO-DO: Implement getX() // 
    //////////////////////////////

    uint8_t res;

    res = (location >> 3);

    return res;
}


uint8_t getY(uint8_t location){
    /* Function that returns the y coordinate from an 8-bit value containing both x and y coordinates.
    Arguments: 
        location: an unsigned 8-bit value representing a location on an 8x32 gameboard.
    Returns: 
        uint8_t representing the y-coordinate (0-7) encoded in the lower 3 bits of the argument.
    */

    //////////////////////////////
    // TO-DO: Implement getY() // 
    //////////////////////////////

    uint8_t res;

    location &= ~(1 << 7);
    location &= ~(1 << 6);
    location &= ~(1 << 5);
    location &= ~(1 << 4);
    location &= ~(1 << 3);

    res = location;
    return res;
    
}


void setX(uint8_t *location, uint8_t new_x){
    /* Function that updates the upper 5 bits of the value stored at location to be equal to new_x.
    Arguments: 
        uint8_t *location: a pointer to an unsigned 8-bit value representing a location on an 8x32 gameboard.
        uint8_t new_x: an unsigned integer representing the value (0-31) that we'd like to set for the x location.
    */

    //////////////////////////////
    // TO-DO: Implement setX() // 
    //////////////////////////////
    //get y val

        uint8_t copy = 0;
    
        copy |= *location; //make a copy of location
            
        copy &= ~(1 << 7); //clear out first 5 bits
        copy &= ~(1 << 6);
        copy &= ~(1 << 5);
        copy &= ~(1 << 4);
        copy &= ~(1 << 3);
    
        //copy is now original y value
     
    
        *location = ((new_x % 32) << 3); //changes 5 msbs, setting new x val

        //now change back y val
        
        *location |= copy;
}


void setY(uint8_t *location, uint8_t new_y){
    /* Function that updates the lower 3 bits of the value stored at location to be equal to new_y.
    Arguments: 
        uint8_t *location: a pointer to an unsigned 8-bit value representing a location on an 8x32 gameboard.
        uint8_t new_y an unsigned integer representing the value (0-7) that we'd like to set for the y location.
    */

    //////////////////////////////
    // TO-DO: Implement setY() // 
    //////////////////////////////
    //get og x val

        uint8_t copy = 0; 
        copy |= *location;
        copy = (*location >> 3);
        
        //copy is now original x value
     
    
        *location = ((new_y % 8)); //changes 3 lsbs, setting new y val

        //now change back y val
        
        *location |= (copy << 3);

}


void setPixel(uint8_t location, uint8_t val){
    /* Function that sets the value of an indivdual pixel (LED) on the display. 	
    Arguments: 	
        location: The location of the LED to be turned on/off on the LED array	
        val: The binary (0 or 1) value indicating if the LED at the location
             should be off (0) or on (1).	
    */	
   
    /////////////////////////////////
    // TO-DO: Implement setPixel() // 
    /////////////////////////////////
    //get x and y values
    uint8_t x_val = getX(location);
    uint8_t y_val = getY(location);

    //update screen buffer with val
    screen_buffer[y_val] &= ~(1 << x_val); //clear, then set
    screen_buffer[y_val] |= (val << x_val);
    
    
}


void drawBoard(struct Snake *snake, uint8_t food){
    /* Function to render the snake and food on the board on each given time-step.
    Arguments:
        struct Snake *snake: pointer to snake struct
        uint8_t food: location of food to render
    */

    //////////////////////////////////
    // TO-DO: Implement drawBoard() // 
    //////////////////////////////////
    eraseBuffer();
    setPixel(food, 1); //turn on food pixel
    //now do for snake body
    for (int i = 0; i < snake->length; i++){
        int temp_loc = snake->body[i];
        setPixel(temp_loc, 1);
    }
    drawBuffer();

}


void updateSnake(struct Snake *snake){
    /* Function to update the snake on each time-step based on its direction.
    Arguments: 
        struct Snake *snake: pointer to snake struct
    */

    ////////////////////////////////////
    // TO-DO: Implement updateSnake() // 
    ////////////////////////////////////


    //original location of head
    uint8_t *head = &snake->body[0]; //this is a pointer


    //get original x,y from head
    uint8_t old_x = getX(snake->body[0]);
    uint8_t old_y = getY(snake->body[0]);

    
    //move the body before the head
    for (int i = snake->length - 1; i > 0; i--){ 
            snake->body[i] = snake->body[i - 1];
        }

    //calculate new x/y val and set the head to new location
    if (snake->direction == up){
        uint8_t new_y = old_y - 1;
        setY(head, new_y); //set new location of the head
        //move rest of snake
        
    }
    if (snake->direction == down){
        uint8_t new_y = old_y + 1;
        setY(head, new_y);
        
    }   
    if (snake->direction == left){
        uint8_t new_x = old_x - 1;
        setX(head, new_x);

        }
    
    if (snake->direction == right){
        uint8_t new_x = old_x + 1;
        setX(head, new_x);
        
        }
    

    
    
}


int generateFood(struct Snake *snake, uint8_t *food){
    /* Function to randomly generate food for the snake.
    Arguments: 
        struct Snake *snake: pointer to snake struct
        uint8_t *food: pointer to variable holding the food's location
    Returns:
        int: 0 if food does not conflict with the snake, 1 if it does.
    */

    int *random_value_ptr = (int*) RANDOM_VALUE_ADDR; // read this address to obtain a random integer value
    //save to temp var only want to look at 8 bits
    uint8_t temp = *random_value_ptr;
    ////////////////////////////////////
    // TO-DO: Complete generateFood() // 
    ////////////////////////////////////

    //check for collisions 
    for (int i = 0; i < snake->length; i++){
        if (temp == snake->body[i]) {
            return 1;
        }}

    //assuming no collisions
    *food = temp;
    return 0;
        
    }
    

uint8_t snakeAteFood(uint8_t *snake_body, uint8_t food){
    /* Function to determine if the snake collided with (and ate) the food.
    Arguments: 
        uint8_t *snake_body: pointer to the snake body array
        uint8_t food: variable holding the food's location
    Returns:
        int: 0 if the snake did not eat the food, 1 if it did.
    */

    /////////////////////////////////////
    // TO-DO: Implement snakeAteFood() // 
    /////////////////////////////////////

    uint8_t head = snake_body[0]; 
    if (head == food){
        return 1;
    }
    else {
        return 0;
    }
}


uint8_t snakeCollisionCheck(struct Snake *snake){
    /* Function to determine if the snake collided with itself.
    Arguments: 
        struct Snake *snake: pointer to snake struct
    Returns:
        int: 0 if the snake did not collide with itself, 1 if it did.
    */

    ////////////////////////////////////////////
    // TO-DO: Implement snakeCollisionCheck() // 
    ////////////////////////////////////////////

    //compare locations
    for (int i = snake->length - 1; i > 0; i--){
        if (snake->body[0] == snake->body[i]){
            return 1;
        }
    }
    //no collisions found
    return 0;
}


void app_main() {
    setup(); // System setup

    // Snake initialization
    struct Snake snake;
    // COMMENT OUT FOR PART 10
    // snake.body[0] = 0;
    // snake.direction = left;
    // snake.length = 1;

   

    //UNCOMMENT FOR PART 10
    for (int i=0; i<3; i++){
        setX(&snake.body[i], 5);
        setY(&snake.body[i], 3-i);
    }
    snake.length = 3;
    snake.direction = left;

    uint8_t food = 0; // food in top right corner of the game board

    while(generateFood(&snake, &food) != 0); // Generate food initially
    drawBoard(&snake, food);

    //initialize current and previous states for all 4 buttons
    int btnl_now = 1; 
    int btnl_prev = 1;
    int btnd_now = 1; 
    int btnd_prev = 1;
    int btnu_now = 1; 
    int btnu_prev = 1;
    int btnr_now = 1; 
    int btnr_prev = 1;
    int btnf_now = 1; 
    int btnf_prev = 1;


    while(1){     
        // printf("entering loop");   

        
        //////////////////////////////////////////////
        // INSERT BUTTON PRESS DETECTION LOGIC HERE //
        //////////////////////////////////////////////

        
        enum snake_direction {up, down, left, right} ;

         //check prev and current states for all 4 buttons
        btnl_prev = btnl_now; //switch around state values
        btnl_now = pinRead(BTNL); // read current state of the button
        btnd_prev = btnd_now; 
        btnd_now = pinRead(BTND); 
        btnu_prev = btnu_now;
        btnu_now = pinRead(BTNU);
        btnr_prev = btnr_now; 
        btnr_now = pinRead(BTNR); 
        btnf_prev = btnf_now; 
        btnf_now = pinRead(BTNF); 



         //check if new button push for each
        if ((btnl_now == 0) && (btnl_prev == 1)){ //want to turn left
            if( snake.direction == left){ //can't turn 180
                snake.direction = left;
            }
            else{
                snake.direction = right;
        }    
        }

        if ((btnd_now == 0) && (btnd_prev == 1)){ //want to turn down
            if( snake.direction == up){ //can't turn 180
                snake.direction = up;
            }
            else{
                snake.direction = down;
        }    
        }

        if ((btnu_now == 0) && (btnu_prev == 1)){//want to turn up
            if( snake.direction == down){ //can't turn 180
                snake.direction = down;
            }
            else{
                snake.direction = up;
        }    
        }
        if ((btnr_now == 0) && (btnr_prev == 1)){//want to turn right
            if( snake.direction == right){ //can't turn 180
                snake.direction = right;
            }
            else{
                snake.direction = left;
        }    
        }

        
        updateSnake(&snake);
        drawBoard(&snake, food);



        if (snakeAteFood(snake.body, food) == 1){
            snake.length = snake.length + 1;

            // Generate food
            while (generateFood(&snake, &food) != 0); // generate food
            
        }
        
        // if snake collided with itself
        if (snakeCollisionCheck(&snake)){
            // printf('snake.body: ', snake.body[0]);

            int leds = 0; //snake decay functionality
            while (leds < snake.length){
                int start = millis();
                while (millis() - start < 200); // One loop iteration every ~200ms
                setPixel(snake.body[leds], 0);
                drawBuffer();
                leds++;
            }
            
            // drawBoard(&snake, 0); //wrong, just draws food at location zero
            while(pinRead(BTNF)){ //SLOW IT DOWN
                int start = millis();
                while (millis() - start < 200); // One loop iteration every ~200ms
            }  //no button push
            // printf('btnf push!');
            
           
            
            //start new game

            // setup();
            snake.length = 3;
            snake.direction = left;
            for (int i=0; i<3; i++){ //initialize head at (5,3)
                setX(&snake.body[i], 5);
                setY(&snake.body[i], 3-i);
            }
            

            // uint8_t food = 0;

            while(generateFood(&snake, &food) != 0); // Generate food initially
            updateSnake(&snake);
            drawBoard(&snake, food);

        }
       
           

        // Code to limit frequency of loop so that gameplay is possible.
        // Put all game code above this point.
        int start = millis();
        while (millis() - start < 200); // One loop iteration every ~200ms
    }
}