.data
    pt:.asciiz "Enter the number whose factorial is to be found "
    fact:.asciiz "The factorial of number is  "  
.text

main:
    la $a0,pt
    li $v0,4
    syscall
    li $v0,5
    syscall 
    
    move $t0, $v0
    li $t1, 1
    li $t2, 1
    factorial_loop:
        mult $t1, $t0
        mflo $t1
        addi $t0, $t0, -1
        bgt $t0, $t2, factorial_loop
        
  lui $t3, 4097
  ori $t3, $t3, 0
  la $a0,fact
  li $v0,4
  syscall
  addi  $a0,$t1,0
  li $v0,1
  syscall