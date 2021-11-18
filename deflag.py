#!/usr/bin/python
import sys

flag = sys.argv[1]
bi_flag = list(bin(int(flag))[2:][::-1])

flag_text = ['     1 : one of the paired reads',
            '     2 : both paired reads mapped well',
            '     4 : unmapped !!!',
            '     8 : the other read unmap',
            '    16 : reverse complement mapped',
            '    32 : the other read reverse complement mapped',
            '    64 : the 1st read of paired reads',
            '   128 : the 2nd read of paired reads',
            '   256 : secondary alignment',
            '   512 : failed filter',
            '  1024 : PCR or optical duplicate',
            '  2048 : supplementary alignment']

print("\n     the meaning of the flag is:\n")

for i in range(len(bi_flag)):
    if bi_flag[i] == '1':
        print(flag_text[i])

print("\n     Have a nice day! :)")