def int_(binary_str):
    if binary_str[0] == '0':
        return int(binary_str, 2)
    elif binary_str[0] == '1':
        flipped_bits = ''.join('1' if bit == '0' else '0' for bit in binary_str[1:])
        return -(int(flipped_bits, 2) + 1)
    
print(int_('00000000000000000000000001101000'))