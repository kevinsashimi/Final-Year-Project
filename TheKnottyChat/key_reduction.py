from Cryptodome.Random import get_random_bytes


predefined_key = '110'

print()
for x in range(3):
    key = ''
    new_key = get_random_bytes(2).hex()

    # Convert hex to binary
    n = int(str(new_key), 16)
    bStr = ''
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    result = bStr

    for i in range(4):
        key += predefined_key + result[i]

    print(f"Generated Key {x + 1}: {key}\n")
