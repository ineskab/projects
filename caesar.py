import sys
import cs50
from cs50 import get_string


# Check that program was run with one command-line argument

if len(sys.argv) != 2:
    print("Usage python caeser.py key")
    exit(1)

# check all characters are digits
while True:
    try:
        k = int(sys.argv[1])
        if k < 0:
            raise ValueError
        break
    except ValueError:
        print("Usage python caeser.py key")

# Prompt user for plaintext

plaintext = get_string("plaintext: ")

# Iterate over each character of the plaintext
print("ciphertext: ", end="")

for c in plaintext:

    # ci = (pi + k) % 26

    if (c.islower()):

        # printf("%c", (tx[i] - 'a' + k) % 26 + 'a');

        print(chr((ord(c) - ord('a') + k) % 26 + ord('a')), end="")

    elif(c.isupper()):

        print(chr((ord(c) - ord('A') + k) % 26 + ord('A')), end="")

    else:

        print(c, end="")

# Print a newline
print()