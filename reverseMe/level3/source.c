#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void    ___syscall_malloc() {
    puts("Nope.");
    exit(1);
}

void    ____syscall_malloc() {
    puts("Good job.");
}

int main() {
    char buff[64];
    char key[9];
    int key_index = 1;
    
    printf("Please enter key: ");
    
    if (scanf("%23s", buff) != 1 || buff[0] != '4' || buff[1] != '2')
        ___syscall_malloc();

    fflush(NULL);
    memset(key, 0, 9);
    key[0] = '*';
    buff[63] = '\0';

    for (size_t i = 2; strlen(key) < 8 && i < strlen(buff); i += 3) {
        char tmp[4] = {
            buff[i],
            buff[i + 1],
            buff[i + 2],
            '\0'
        };
        int num = atoi(tmp);
        key[key_index] = (char)num;
        ++key_index;
    }
    key[key_index] = '\0';
    switch(strcmp(key, "********")) {
        case -2:
            ___syscall_malloc();
            break;
        case -1:
            ___syscall_malloc();
            break;
        case 0:
            ____syscall_malloc();
            break;
        case 1:
            ___syscall_malloc();
            break;
        case 2:
            ___syscall_malloc();
            break;
        case 3:
            ___syscall_malloc();
            break;
        case 4:
            ___syscall_malloc();
            break;
        case 5:
            ___syscall_malloc();
            break;
        case 115:
            ___syscall_malloc();
            break;
        default:
            ___syscall_malloc();
            break;
    }
    return 0;
}