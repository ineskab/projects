from cs50 import get_int

# Prompt user for a positive number
while True:
    n = get_int("Write the number between 1 and 8: ")
    if n > 0 and n <= 8:
        break

for i in range(n):
    print("#"*(i + 1))
print()
