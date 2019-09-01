#include <cs50.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

int shift(char c);

int main(int argc, string argv[])
{
    if (argc == 2)
    {
        string k = argv[1];
        int lenk = strlen(k);
        for (int i = 0; i < lenk; i++)
        {
            if (isalpha(k[i]) == 0)
            {
                printf("Usage: ./vigenere keyword\n");
                return 1;
            }
        }
        string tx = get_string("plaintext: ");
        printf("ciphertext: ");

        for (int i = 0, ke = 0;  i < strlen(tx); i++)
        {
            int sh = shift(argv[1][ke]);

            if (islower(tx[i]))
            {
                printf("%c", (tx[i] - 'a' + sh) % 26 + 'a');
            }
            else if (isupper(tx[i]))
            {
                printf("%c", (tx[i] - 'A' + sh) % 26 + 'A');
            }
            else if (i > 32 || i < 64)
            {
                printf("%c", tx[i]);
            }
            ke = (ke + 1) % lenk ;
        }  
        printf("\n");
        return 0;
    }
    else
    {
    printf("Usage: ./vigenere keyword\n");
    return 1;
    }
}

int shift(char c)
{
    return (int) toupper(c) - 'A';
}
