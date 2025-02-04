import requests
from Barcode import Barcode, scan_barcode

# InvenTree API settings
BASE_URL = "http://inventory.local/api"
API_TOKEN = "inv-d800a512df3a4c3365327b39298bcfe51782d83e-20250202"

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def get_stock_entries(part_id):
    """Fetch all stock entries for a given part ID."""
    url = f"{BASE_URL}/stock/?part={part_id}"
    response = requests.get(url, headers=HEADERS)
    print(response)
    if response.status_code == 200:
        stock_entries = response.json()
        print(stock_entries)
        return stock_entries  # Return all stock entries
    return []


def update_stock(stock_entry_id, new_quantity):
    """Update stock quantity for a specific stock entry."""
    url = f"{BASE_URL}/stock/{stock_entry_id}/"
    payload = {"quantity": new_quantity}
    
    response = requests.patch(url, json=payload, headers=HEADERS)
    
    if response.status_code in [200, 204]:  # 200 OK or 204 No Content
        print(f"Stock updated successfully: ID {stock_entry_id}, New Quantity: {new_quantity}")
        return True
    else:
        print(f"Failed to update stock: {response.status_code}, {response.text}")
        return False


# Example usage

while True:
    barcode = scan_barcode()
    if barcode.type == "part":
        part_id = barcode.data
        break
    elif barcode.type == "command":
        command = barcode.data
        if command == "exit":
            print("Quitting!")
            exit()
    else:
        print("Invalid barcode scanned. Please scan again.")

if part_id:
    stock_entries = get_stock_entries(part_id)

    if stock_entries:
        # Select the first available stock entry
        stock_entry = stock_entries[0]
        if len(stock_entries) > 1:
            print("Multiple stock entries found. Please scan the stock label:")
            for entry in stock_entries:
                print(f"ID: {entry['pk']}, Quantity: {entry['quantity']}, Location: {entry.get('location', 'N/A')}")
            
            while True:
                stock_entry_id = eval(input("Scan Barcode: ")).get("stockitem")
                if stock_entry_id:
                    break
                else:
                    print("Invalid barcode scanned. Scan the STOCK barcode. It shouldn't have any text.")
            

        else:
            stock_entry = stock_entries[0]
            stock_entry_id = stock_entry["pk"]

        
        current_quantity = stock_entry["quantity"]

        if current_quantity > 0:
            new_quantity = current_quantity - 1
            update_stock(stock_entry_id, new_quantity)
        else:
            print(f"Stock for part '{part_id}' is already at zero.")
    else:
        print(f"No stock entries found for part '{part_id}'.")
else:
    print(f"Part '{part_id}' not found.")
