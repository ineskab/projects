from cs50 import get_string
from sys import argv
import sys


def main():
     # Accepts as its sole command-line argument the name (or path) of a dictionary of banned words (i.e., text file).
    if len(sys.argv) != 2:
        print("Usage: python bleep.py dictionary")
        exit(1)

    banned_words = set()

    with open(argv[1], "r") as file:
        for line in file:
            banned_words.add(line.strip("\n").lower())

    # Prompts the user to provide a mesage
    message = get_string("What message would you like to censor? ")
    # Tokenizes that message into its individual component words
    words = message.split()
    output = ""
    # Iterates over the list of "tokens" (words) that is returned by calling split
    for word in words:
        if word.lower() in banned_words:
            output += len(word) * "*" + " "
        else:
            output += word + " "
    # Print back the censored message, i.e. banned words characters present in the message will be replaced with "*")
    print(output.strip())
    return 0


if __name__ == "__main__":
    main()
