#include <stdio.h>
#include <string.h>

int main() {
    char str[10];
    char *mdp = "__stack_ckeck";

    printf("Please enter key: ");
    scanf("%s", str);
    if (strcmp(str, mdp))
        printf("Nope.\n");
    else
        printf("Good Job.\n");
    return 0;
}