.data 
    next_line:.asciiz "\n"
    option:.asciiz "Welcome to ROT13 Encryption - Decryption.\nEnter 1 for encryption and 2 for decryption. "
    print_input_string:.asciiz "Enter the input string to be encoded.  "
    buffer:.space 256

.text

#printing the option menu
li $v0, 4
la $a0, option
syscall
 
#menu 
li $v0, 5
syscall
move $t2, $v0

#check if the input is 1 or 2
beq $t2, 1, encrypt
beq $t2, 2, decrypt
j exit
 

    

encrypt:
    #printing the input string
    li $v0, 4
    la $a0, print_input_string
    syscall


    #input string , equivalent to fgets of C
    li $v0, 8
    la $a0, buffer
    li $a1, 256
    syscall


    #copying the address of input string to $t7, $t5 and $t9
    move $t7,$a0
    move $t5,$a0
    move $t9,$a0
    li $t4,65

    #while loop    
    jal whileencrypt
    whileencrypt:
        lb $t4 , 0($t7)
        beq $t4 , 0x0A, loopend
        beq $t4 , 0x0, loopend
        beq $t4 , 0x20, update_pointers
        bgt $t4, 96, small_temp
        bgt $t4, 64, caps_temp
        j update_pointers
        caps_temp:
            blt $t4,91,caps
            j update_pointers
            caps:
                move $t1, $t4
                addi $t1, $t1, -64
                addi $t1, $t1, 13
                # addi $t1, $t1, 26
                li $s6,26
                div $t1,$s6
                mfhi $t0
                addi $t0, $t0, 64
                sb $t0, 0($t5)
                j update_pointers

        small_temp:
            blt $t4,123,small
            j update_pointers
            small:
                move $t1, $t4
                addi $t1, $t1, -96
                addi $t1, $t1, 13
                # addi $t1, $t1, 26
                li $s6,26
                div $t1,$s6
                mfhi $t0
                addi $t0, $t0, 96
                sb $t0, 0($t5)
                j update_pointers

        update_pointers:
            addi $t7, $t7, 1
            addi $t5, $t5, 1
        j whileencrypt


    loopend:  

        j print_string

decrypt:

    #printing the input string
    li $v0, 4
    la $a0, print_input_string
    syscall


    #input string , equivalent to fgets of C
    li $v0, 8
    la $a0, buffer
    li $a1, 256
    syscall


    #copying the address of input string to $t7, $t5 and $t9
    move $t7,$a0
    move $t5,$a0
    move $t9,$a0
    li $t4,65
    #while loop
    jal whiledecrypt
    whiledecrypt:
        lb $t4 , 0($t7)
        beq $t4 , 0x0A, loopend2
        beq $t4 , 0x0, loopend2
        beq $t4 , 0x20, update_pointers2
        bgt $t4, 96, small_temp2
        bgt $t4, 64, caps_temp2
        j update_pointers2
        caps_temp2:
            blt $t4,91,caps2
            j update_pointers2
            caps2:
                move $t1, $t4
                addi $t1, $t1, -64
                addi $t1, $t1, -13
                addi $t1, $t1, 26
                li $s6,26
                div $t1,$s6
                mfhi $t0
                addi $t0, $t0, 64
                sb $t0, 0($t5)
                j update_pointers2

        small_temp2:
            blt $t4,123,small
            j update_pointers2
            small2:
                move $t1, $t4
                addi $t1, $t1, -96
                addi $t1, $t1, -13
                addi $t1, $t1, 26
                li $s6,26
                div $t1,$s6
                mfhi $t0
                addi $t0, $t0, 96
                sb $t0, 0($t5)
                j update_pointers2

        update_pointers2:
            addi $t7, $t7, 1
            addi $t5, $t5, 1
        j whiledecrypt

    loopend2:
        j print_string


print_string:
    #printing the input string
    li $v0, 4
    move $a0, $t9 
    syscall
    j exit


exit:
    li $v0, 10
    syscall
