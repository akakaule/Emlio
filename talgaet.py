# Talgætteri - computeren tænker på et tal, du skal gætte det

import random

hemmeligt_tal = random.randint(1, 100)
antal_gaet = 0

print("Jeg tænker på et tal mellem 1 og 100.")
print("Kan du gætte det?")

while True:
    svar = input("Dit gæt: ")
    gaet = int(svar)
    antal_gaet = antal_gaet + 1

    if gaet < hemmeligt_tal:
        print("For lavt! Prøv igen.")
    elif gaet > hemmeligt_tal:
        print("For højt! Prøv igen.")
    else:
        print(f"Tillykke! Du gættede det på {antal_gaet} forsøg.")
        break
