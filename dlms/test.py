import random

def generate_challenge(authentication, size):
    r = random.Random()  # Initialize a random number generator
    length = size  # Set the length of the challenge to the specified size

    result = bytearray()  # Create a byte array to store the challenge

    # Populate the byte array with random byte values
    for _ in range(length):
        result.append(r.randint(0, 121))  # Random byte value between 0 and 121 (inclusive)

    return result  # Return the generated challenge byte array

# Generate a challenge of size 16 for HighECDSA authentication
challenge = generate_challenge(1, 16)



formatted_hex_uppercase = ' '.join([f'{byte:02X}' for byte in challenge])
# Print the challenge bytes with space between each byte
print(formatted_hex_uppercase)
