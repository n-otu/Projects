.section .text      # indicates a code segment
.align 2            # specifies how data should be arranged in memory
.globl pinSetup   # makes pinSetup able to be used outside of this file
.globl pinWrite     # makes pinWrite able to be used outside of this file
.globl pinRead      # makes pinRead able to be used outside of this file
.globl setPixel     # makes setPixel able to be used outside of this file
.globl eraseBuffer  # makes eraseBuffer able to be used outside of this file

# C declaration: int pinRead(int pin_num)
# ARGUMENTS a0: pin_num
# RETURNS bit read from GPIO pin
pinRead:
    lui a2, 0x60004 # load value 0x60004 into register a2 (a2 = 0x60004)
    addi a2, a2, 0x3C # GPIO_IN_ADDR, or (a2 <- a2 + 0x3C)
    
    # my code
    #load pin_num from a0 into register a3
    #lui a0, 0x6000403C
    lw a3, 0(a2)
    
    srl a4, a3, a0  # do right shift of a3 by pin_num in a0, store in a4
    andi a4, a4, 1 # and with 1, result is a0
    addi a0, a4, 0 #put a4 in a0
    sw a0, 0(a2) # store a2 result in a0
    
    
    # store in a3
    # shift a3 by right by pin num
    # store in a4, not a0

    
    # c implementation
    #int* input_val = (int*) GPIO_IN_ADDR;
    #int bit = (*input_val >> pin_num) & 1; //read value using bitwise op
    #return bit; // replace 0 with return value of pinRead
    
    

    jalr x0, 0(ra) #return a0



# C declaration: void pinWrite(int pin_num, int value)
# ARGUMENTS a0: pin_num, a1: value
# RETURNS: Nothing
pinWrite:
    lui a2, 0x60004 # loads value 0x60004 into a2
    addi a2, a2, 0x4  # GPIO_OUT_ADDR (a2 <- a2 + 0x4)

    

    # assembly version
    
    #load value stored at gpio from a2 into register a3
    lw a3, 0(a2)
    
    # register a7 just equal to 1
    addi a7, x0, 1
    
    
     # make sure value stored at a1 is 1
     sltu a5, x0, a1
     add a1, x0, a5
     # left shift 1 by pin_num, store in a4
     sll a4, a7, a0
     # clear bit at pin_num
     xori a4, a4, -1
     # do &= part with value and 1 shifted
     and a6, a3, a4
     # set final value with or and a shift
     sll a5, a1, a0
     or a3, a5, a6
     
     # store a2 result back in a0
     sw a3, 0(a2) 

    jalr x0, 0(ra)

# C declaration: void pinSetup(int pin_num, int mode)
# ARGUMENTS a0: pin_num, a1: mode
# RETURNS: Nothing
pinSetup:
    lui a2, 0x60009
    addi a2, a2, 0x4  # IO_MUX_GPIOn_ADDR

    lui a3, 0x60004
    addi a3, a3, 0x20 # GPIO_ENABLE_ADDR
    
   
    # register a7 just equal to 1
    addi a7, x0, 1
    
    
    beq a1, a7, output # go to output if mode == GPIO_OUTPUT, else continue
    slli a0, a0, 2    # 4*pin_num is same as shifting left by 2 in base 2
    add a4, a0, a2    # (IO_MUX_GPIOn_ADDR + (4*pin_num), storevalue in a4
    
    
    lw a6, 0(a4)      # load value at a4
    slli a5, a7, 8    # shift 1 left by 8, store in a5
    or a6, a6, a5     # perform |= operation
    
    # reset a7 to 1
    xori a7, a7, -1
    addi a7, x0, 1
    
    slli a7, a7, 9    # repeat but with 9 left shift
    or a6, a6, a7
    
    sw a6, 0(a4) # store value back in a4
    
    jalr x0, 0(ra)
    
    output:
    lw a6, 0(a3)      # load value at a3
    sll a5, a7, a0    # (1 << pin_num)
    or a6, a5, a6
    sw a6, 0(a3) # store value back in a4
   
    jalr x0, 0(ra)



# C declaration: void setPixel(uint32_t* screen_buffer_addr, uint8_t x, uint8_t y, uint8_t val);
# ARGUMENTS a0: screen_buffer base address, a1: x, a2: y, a3: val
# RETURNS: Nothing
setPixel:
    
    #or a4, a1, a2 # get x and y location, store in a4
    slli a2, a2, 2 # get 4 * memory loc of y, store in a2
    add a2, a0, a2 # add w/ base address, store in a2
    lw a5, 0(a2) # load value stored at address into a5
    
    # initialize a7 as 1
    addi a7, x0, 1
    
    # now modify array value directly

    # left shift 1 by x, store in a7
     sll a7, a7, a1
    # clear bit at x
     xori a7, a7, -1
   # do &= part with value and 1 shifted, store in a7
     and a7, a5, a7
   # set final value with or and a shift
     sll a4, a3, a1
     or a6, a7, a4
     
    
    sw a6, 0(a2) # set value at location   
    

    jalr x0, 0(ra)

# C declaration: void eraseBuffer(uint32_t* screen_buffer_addr)
# ARGUMENTS a0: screen_buffer base address
# RETURNS: Nothing

eraseBuffer:
    addi a1, x0, 8      # upper bound on for loop
    addi a2, x0, 0      # "i" for for loop
looping:
    slli a3, a2, 2      # calculate 4*i
    add a4, a0, a3      # get address of array element by adding base address + 4*i
    sw zero, 0(a4)      # write 0 to memory address
    addi a2, a2, 1      # increment i
    bne a2, a1, looping # continue looping if i < 8
    jalr x0, 0(ra)      # return from eraseBuffer



    