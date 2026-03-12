original_wordlist = open("wordlist.txt", "r")
custom_wordlist = open("custom.txt", "w")

print("Generating custom wordlist for user hakanbey...")

for line in original_wordlist:
    password = "123adana" + line
    custom_wordlist.write(password)

original_wordlist.close()
custom_wordlist.close()

print("Wordlist generated inside custom.txt !")
