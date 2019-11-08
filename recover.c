#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>


int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover image\n");
        return 1;
    }

    // remember filenames
    char *input = argv[1];
    // open card.raw
    FILE *cardptr = fopen(input, "r");
    if (cardptr == NULL)
    {
        fprintf(stderr, "file couldn't found  %s.\n", input);
        return 2;
    }
    // create buffer
    unsigned char buffer[512];

    int file_counter = 0;
    FILE *new_jpg;
    //read 512 bytes into a buffer repeat untile end of a card
    while (fread(buffer, 512, 1, cardptr) == 1)
    {
        // if we found signature
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xe0) == 0xe0)
        {
            if (file_counter > 0)
            {
                fclose(new_jpg);
            }
            //open new file
            char filename[8];
            sprintf(filename, "%03d.jpg", file_counter++);
            new_jpg = fopen(filename, "w");
            //write to new jpg
            fwrite(buffer, 512, 1,  new_jpg);
        }
        // if we didn't find signature
        else
        {
            if (file_counter > 0)
            {
                fwrite(buffer, 512, 1, new_jpg);
            }
        }
    }
    fclose(new_jpg);
    fclose(cardptr);
    return 0;
}
