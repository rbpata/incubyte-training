# 9. Count vowels in string
s = "ram"
vowels = "aeiou"
count = sum(1 for c in s if c in vowels)
print(count)
