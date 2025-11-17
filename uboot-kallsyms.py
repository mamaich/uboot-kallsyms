import sys

def main(input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()

    # The signature to search for (first symbol entry without null)
    signature = b'0000000000000000__image_copy_start'
    
    # Find the start position of the symbol table
    start_pos = data.find(signature)
    if start_pos == -1:
        raise ValueError("Symbol table not found in the file.")

    # Adjust to include the full first entry (signature is without null, but entry has null after)
    # We need to find the end of the first string
    pos = start_pos
    entries = []

    while True:
        # Find the next null byte
        null_pos = data.find(b'\x00', pos)
        if null_pos == -1:
            raise ValueError("Invalid symbol table format: no null terminator found.")

        # Extract the string bytes (excluding null)
        string_bytes = data[pos:null_pos]
        
        # If empty string (pos == null_pos), end of table
        if len(string_bytes) == 0:
            break

        # Decode to string (assuming ASCII)
        try:
            symbol_str = string_bytes.decode('ascii')
        except UnicodeDecodeError:
            raise ValueError("Non-ASCII characters in symbol table.")

        # Parse: first 16 chars hex address, rest name
        if len(symbol_str) < 16:
            raise ValueError("Invalid symbol entry: too short.")
        
        address_hex = symbol_str[:16]
        name = symbol_str[16:]
        
        # Validate address is hex
        try:
            int(address_hex, 16)
        except ValueError:
            raise ValueError(f"Invalid hex address: {address_hex}")

        entries.append((address_hex, name))
        
        # Move to next entry
        pos = null_pos + 1

    # Write to output file in IDC script format
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('#include <idc.idc>\n')
        f.write('#define BASE_ADDR 0x10000000\n')
        f.write('static main(void)\n')
        f.write('{\n')
        for address, name in entries:
            f.write(f'  set_name(BASE_ADDR + 0x{address}, "{name}");\n')
        f.write('}\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_binary_file> <output_text_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        main(input_file, output_file)
        print("Symbol table extracted successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
