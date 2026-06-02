def create_32kb_bin(input_file, output_file):
    # Target size in bytes (32KB)
    target_size = 40 * 1024  # 32KB = 32768 bytes

    # Read the original binary file
    with open(input_file, 'rb') as f:
        original_data = f.read()

    # Calculate the number of padding bytes needed
    original_size = len(original_data)
    padding_size = target_size - original_size

    if padding_size < 0:
        raise ValueError(f"The input file is larger than 32KB (size: {original_size} bytes)")

    # Create the padding with 0xFF
    padding = bytes([0xFF] * padding_size)

    # Create the new binary data with padding
    new_data = original_data + padding

    # Write the new data to the output file
    with open(output_file, 'wb') as f:
        f.write(new_data)

    # Confirm the size of the new file
    new_size = len(new_data)
    print(f"New file size: {new_size} bytes")

# Example usage
input_file = 'STM32G070RBT6_APP2.bin'  # Replace with your binary file
output_file = 'STM32G070RBT6_APP2_40kb.bin'  # The resulting 32KB file
create_32kb_bin(input_file, output_file)
