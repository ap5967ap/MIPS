li $t2,2
#check if the input is 1 or 2
beq $t2, 1, encrypt
beq $t2, 2, decrypt
j exit
 

encrypt:
    
    #input string , equivalent to fgets of C
    li $s6,0x10010000
    li $s7,0x10010001
    li $t8,0x10010002
    li $t9,0x10010003
    li $t0,0x10010004
    li $s1,'h'
    li $s2,'e'
    li $s3,'l'
    li $s4,'l'
    li $s5,'o'
    sb $s1,0($s6)
    sb $s2,0($s7)
    sb $s3,0($t8)
    sb $s4,0($t9)
    sb $s5,0($t0)
    add $a0,$0,$s6
    #copying the address of input string to $t7, $t5 and $t9
    move $t7,$a0
    move $t5,$a0
    move $t9,$a0
    li $t4,65

    #while loop    
    j whileencrypt
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

        j exit

decrypt:
    
    #input string , equivalent to fgets of C
    li $s6,0x10010000
    li $s7,0x10010001
    li $t8,0x10010002
    li $t9,0x10010003
    li $t0,0x10010004
    li $s1,'u'
    li $s2,'r'
    li $s3,'y'
    li $s4,'y'
    li $s5,'b'
    sb $s1,0($s6)
    sb $s2,0($s7)
    sb $s3,0($t8)
    sb $s4,0($t9)
    sb $s5,0($t0)
    add $a0,$0,$s6
    
    #copying the address of input string to $t7, $t5 and $t9
    move $t7,$a0
    move $t5,$a0
    move $t9,$a0
    li $t4,65
    #while loop
    j whiledecrypt
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
        j exit




exit:
    
