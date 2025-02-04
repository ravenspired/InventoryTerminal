import json

class Barcode:
    def __init__(self, barcode_str: str):
        try:
            barcode_data = json.loads(barcode_str)
            if isinstance(barcode_data, dict):
                key = next(iter(barcode_data))  # Get the first key dynamically
                self.type = str(key)
                self.data = str(barcode_data[key])
            else:
                self.type = None
                self.data = None
                print("Data isn't a dictionary")
                #raise ValueError("Invalid barcode format")
        except (json.JSONDecodeError, ValueError) as e:
            self.type = None
            self.data = None
            print("Error parsing barcode: {e}")
            #raise ValueError(f"Error parsing barcode: {e}")

    def __repr__(self):
        return f"Barcode(type='{self.type}', data='{self.data}')"

def scan_barcode():
    try:
        barcode_str = input("Scan a barcode: ")  # Reads input from the scanner
        return Barcode(barcode_str)
    except ValueError as e:
        print(e)
        return None
