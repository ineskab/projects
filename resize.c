// Copies a BMP file

#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: copy infile outfile\n");
        return 1;
    }
    // declearing n
    int n = atoi(argv[1]);
    if (n < 1 || n > 100)
    {
        printf("Factor must be in the range 1-100\n");
        return 1;
    }


    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;

    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }
    // determine new size
    int inWidth = bi.biWidth;
    int inHeight = abs(bi.biHeight);
    int outWidth = inWidth * n;
    int outHeight = inHeight * n;

    // determine padding for scanlines
    int inPadding = (4 - (inWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int outPadding = (4 - (outWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    // reconfigure headers
    bi.biHeight = -1 * outHeight;
    bi.biWidth = outWidth;
    bi.biSizeImage = ((sizeof(RGBTRIPLE) * outWidth) + outPadding) * abs(outHeight);
    bf.bfSize = bi.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi, sizeof(BITMAPINFOHEADER), 1, outptr);

    RGBTRIPLE *outScanLine = malloc(outWidth * sizeof(RGBTRIPLE));

    if (outScanLine == NULL)
    {
        fprintf(stderr, "Not enough memory for resizing the image.");
        return 5;
    }

    // iterate over infile's scanlines
    for (int i = 0; i < inHeight; i++)
    {
        int arrow = 0;

        // iterate over pixels in the scanline
        for (int j = 0; j < inWidth; j++)
        {
            // temporary storage
            RGBTRIPLE triple;

            // read RGB triple from infile
            fread(&triple, sizeof(RGBTRIPLE), 1, inptr);

            for (int k = 0; k < n; k++)
            {
                outScanLine[arrow] = triple;
                arrow += 1;
            }
        }

        for (int l = 0; l < n; l++)
        {
            //fwrite(&outScanLine, sizeof(outScanLine), 1, outptr);

            for (int p = 0; p < outWidth; p++)
            {
                fwrite(&outScanLine[p], sizeof(RGBTRIPLE), 1, outptr);
            }

            // write padding to outfile
            for (int k = 0; k < outPadding; k++)
            {
                fputc(0x00, outptr);
            }
        }

        // skip over padding, if any
        fseek(inptr, inPadding, SEEK_CUR);

    }

    // free memory
    free(outScanLine);

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}
