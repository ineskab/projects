# Questions



stdint.h (Standard Integer Types) is a header file in the C standard library that provides a set of typedefs integer types having specified widths and defines corresponding sets of macros. And the defined minimum and maximum allowable values for each type, using macros.


They are a cross-platform integer types, so they behave identically across multiple platforms. uint8_t is an unsigned int of 8 bits, the range is from 0 to 255 decimal. uint32_t is an unsigned int , the range is from 0 to 4294967295 decimal. int32_t is a  32-bit signed integer (range: –2147483648 to 2147483647 decimal) uint16_t is an unsigned int16, the range is from 0 to 65535 decimal.



BYTE: 1 byt, DWORD: 4 byte,  LONG: 4 bytes,  WORD: 2 bytes


## What (in ASCII, decimal, or hexadecimal) must the first two bytes of any BMP file be? Leading bytes used to identify file formats (with high probability) are generally called "magic numbers."

The first two bytes specify the file is a bitmap with the words "BM", or the hex 0x4D42

## What's the difference between `bfSize` and `biSize`?

bfSize is the size, in bytes, of a bitmap file. biSize specifies the number of bytes required by the structure.

## What does it mean if `biHeight` is negative?

If biHeight is negative, the bitmap is a top-down DIB and its origin is the upper-left corner.

## What field in `BITMAPINFOHEADER` specifies the BMP's color depth (i.e., bits per pixel)?

biBitCount

## Why might `fopen` return `NULL` in `copy.c`?

fopen will return null if it cannot open the file, for example, if there is not enough memory or the file can not be found.

## Why is the third argument to `fread` always `1` in our code?

The third argument of fread is the number of elements, each one with a size of size bytes. Since function is looking through each struct one at a time the third argument is 1 every time.

## What value does `copy.c` assign to `padding` if `bi.biWidth` is `3`?

3

## What does `fseek` do?

This function moves the file pointer to specified location, specified by the number of bytes.

## What is `SEEK_CUR`?

Current position of the file pointer
