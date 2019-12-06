from cs50 import get_float

# Prompt user for a positive number
while True:
    change = get_float("Change owed:")
    if change > 0:
        break

n = round(change * 100)

quarter_count = (n//25)
dimes_count = ((n - quarter_count*25)//10)
nickels_count = ((n-quarter_count*25 - dimes_count*10)//5)
pennies_count = ((n-quarter_count*25 - dimes_count*10 - nickels_count*5))
total = (quarter_count + dimes_count + nickels_count + pennies_count)
print(total)