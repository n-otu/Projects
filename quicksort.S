.section .text     
.align 2 
.globl quicksort

quicksort:

    addi sp, sp, -20
    sw ra, 0(sp) # og address
    sw s0, 4(sp) # store each of the values at diff offsets
    sw s1, 8(sp) 
    sw s2, 12(sp)
    sw s3, 16(sp)
    
    
    mv s0, a0 
    mv s1, a1  
    mv s2, a2 
     
    bge     a1, a2, done   
    call    partition  # result becomes a0 
    
    mv s3, a0 # save q value in s3
    mv a2, a0
    addi a2, a2, -1  # end becomes q-1 
    mv a0, s0 # p for quicksort
    mv a1, s1 # start 
    call  quicksort        
    call arrayViz    

    mv a0, s0 # p for quicksort
    mv a1, s3
    addi a1, a1, 1  # start becomes q + 1
    mv a2, s2
    call    quicksort    
    call arrayViz   
done:
    lw ra, 0(sp) # now put everything back
    lw s0, 4(sp) 
    lw s1, 8(sp)
    lw s2, 12(sp)
    lw s3, 16(sp)
    addi sp, sp, 20
     
    ret


partition:
    slli t0, a2, 2 # 4 * end
    add t0, a0, t0 # address of p[end]
    lw t1, 0(t0) # p[end] inside t1

    addi t2, a1, -1 # t2/i = start -1 
    add t3, a1, zero # j = start for loop

loop:
    bge t3, a2, end  # if j >= end, exit loop
    slli t4, t3, 2 # 4 * j
    add t4, a0, t4 # address of j
    lw a4, 0(t4) # p[j]

    blt t1, a4, else # if p[j] > x, go to else branch
    # swap p[i+1] and p[j]
    addi t2, t2, 1    # i += 1
    
    slli t5, t2, 2 # 4 * i
    add t5, a0, t5 # address of i
    lw a5, 0(t5) # p[i] in a5
    sw a5, 0(t4) # put p[i] at j
    sw a4, 0(t5) # put p[j] at i

else:
    addi t3, t3, 1    # j += 1
    j loop

end:
    addi t2, t2, 1    # i + 1
    slli t6, t2, 2  # (i + 1) * 4
    add t6, a0, t6 # address of i + 1
    lw a6, 0(t6)   # put p[i+1] in a6
    sw a6, 0(t0)  # p[end] = tmp
    sw t1, 0(t6)  # p[i + 1] = p[end];
    mv a0, t2 # put i + 1 in right place for return
  
    ret