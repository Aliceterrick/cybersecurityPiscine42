This projet aims to disasemble binary files to find passwords, and then rewrite the source code using C.
For that, we will use gdb and radare2.
Usefull commands for gdb:

''' disas func_name ''' to see the asm of this function
''' x/s var_name ''' to see the value of variable at the moment
''' break *break_point''' to place a breakpoint where the run command will stop the execution.
'''run''' to run the program

Usefull commands for radare2:

'''s OxXXX/func_name''' to analyze speficic point
'''pdf''' to print disasembled current function
''' wa instruc''' to modify the binary at the current point (for a file opened with the -w option)

The bonus part aims to patch the binaries in order to let's them accept all passwords. For this we use radare2, and we have several options :
-for level 1 we simply overwrite the call to strcmp with mov eax, 0 in order to set the comparison value to 0, that will every time trigger the success behavior.
-for both level 2 and 3 we have an additional difficulty : there are more than one exit possible. The easiest way seems to be overwrite the jne instructions after comparisions, to avoid fail behavior. For level 3 we also overwrite the behavior of strcmp (another way to do same things that for level 1). Now strcmp simply return 0.