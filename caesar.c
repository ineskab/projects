#include <cs50.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

int main(int argc, string argv[])
{
    if (argc == 2)
    {
        if ((atoi(argv[1]) == 0) && (strcmp(argv[1], "0") != 0))
        {
            printf("Usage: ./caesar key\n");
            return 1;
        }
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }

    string tx = get_string("plaintext: ");
    int k = atoi(argv[1]);
    printf("ciphertext: ");
    for (int i = 0, len = strlen(tx); i < len; i++)
    {
        if (islower(tx[i]))
        {
            printf("%c", (tx[i] - 'a' + k) % 26 + 'a');
        }
        else if (isupper(tx[i]))
        {
            printf("%c", (tx[i] - 'A' + k) % 26 + 'A');
        }
        else if (i > 32 || i < 64)
        {
            printf("%c", tx[i]);
        }
    }  

    printf("\n");

}  


        

