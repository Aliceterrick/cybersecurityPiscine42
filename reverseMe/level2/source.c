#include <stdio.h>
#include <string.h>
#include <stdlib.h>

void no() {
    puts("Nope.");
    exit(1);
}
void ok() { 
    puts("Good job.");
}

int main() {
    char input[100];
    char key[9] = {0}; 
    
    printf("Please enter key: ");
    if (scanf("%s", input) != 1) {
        no();
        return 1;
    }

    if (input[0] != '0' || input[1] != '0') {
        no();
        return 1;
    }

    fflush(NULL);
    memset(key, 0, 9);
    key[0] = 'd';
    size_t inp_index = 2;
    size_t key_index = 1;

    while (strlen(key) < 8 && inp_index < strlen(input)) {
        char block[4] = {
            input[inp_index],
            input[inp_index + 1],
            input[inp_index + 2],
            '\0'
        };
        
        int num = atoi(block);
        key[key_index] = (char)num;
        
        inp_index += 3;
        ++key_index;
    }
    key[key_index] = '\0';
    if (strcmp(key, key) == 0)
        ok();
    else
        no();
    return 0;
}