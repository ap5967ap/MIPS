li $t0,5
li $s0,1 #s0 contains the answer
fact:
	beq $t0,$0,exit
	mult $s0,$t0
	mflo $s0
	addi $t0,$t0,-1
	j fact
exit:
