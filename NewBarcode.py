


def scan_barcode(instruction=[]):
    while True:
        try:
            user_input = input("Scan barcode: ")
            barcode_data = eval(user_input)  # Convert input to dictionary (use `json.loads` if input is JSON string)
            
            if not isinstance(barcode_data, dict) or len(barcode_data) != 1:
                print("Invalid input. Please enter a dictionary with one key-value pair.")
                continue
            
            key, value = list(barcode_data.items())[0]
            
            if key not in instruction:
                print(f"Mismatch: '{key}' is not in the instruction list. Try again.")
                continue
            
            if isinstance(key, str) and key.isdigit():
                key = int(key)  # Convert key to int if it's a numeric string
            
            if isinstance(value, str) and value.isdigit():
                value = int(value)  # Convert value to int if it's a numeric string
                
            return key, value
        
        except Exception as e:
            print("Error processing input. Ensure you enter a valid dictionary format.")
