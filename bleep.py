from cs50 import get_string
from sys import argv
import sys

def main():
     # Accepts as its sole command-line argument the name (or path) of a dictionary of banned words (i.e., text file).
    if len(sys.argv) != 2:
        print("Usage: python bleep.py dictionary")
        exit(1)

    file = open(argv[1])
    BannedWords = set()

    for line in file:
        BannedWords.add(line.strip("\n").lower())

    message = get_string("What message would you like to censor? ")
    x = message.split()
    outputString = ""

    for word in x:
        if word.lower() in BannedWords:
            outputString += "*" * len(word) + " "
        else:
            outputString += word + " "
    print(outputString.strip())

if __name__ == "__main__":
    main()
