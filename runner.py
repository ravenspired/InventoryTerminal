import requests
from NewBarcode import scan_barcode
from Stack import Stack


def run():
    # InvenTree API settings
    BASE_URL = "http://inventory.local/api"
    print("Scan your ID card")
    _,API_TOKEN = scan_barcode(["api"])

    # Headers for authentication
    HEADERS = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json"
    }

    def fetch_data(endpoint):
        """Generic function to fetch data from the InvenTree API"""
        url = f"{BASE_URL}/{endpoint}/"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
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
        

    def get_part_by_id(part_id):
        """Retrieve a part by its ID"""
        return next((part for part in parts if part['pk'] == part_id), None)

    def get_stock_by_id(stock_id):
        """Retrieve stock by its ID"""
        return next((stock for stock in stocks if stock['pk'] == stock_id), None)


    def print_action_queue():
        """Prints the action queue after each scan."""
        print("Scanned Items:\n")
        print("Quantity | Item Name | Item ID | Stock ID")
        print("-------------------------------------------")
        for stock_id, (quantity, part_id) in action_queue.items():
            part = get_part_by_id(part_id)
            print(f"{quantity} | {part['name']} | {part_id} | {stock_id}")
        print("\n")




    # Fetch initial data
    print("Please wait, contacting server...")
    parts = fetch_data("part")
    stocks = fetch_data("stock")
    print("Done")


    action_queue = {}
    active = True
    command = "subtract"


    while active:
        print(f"Please scan PART or STOCKITEM code. CURRENT COMMAND: {command}")
        item_type, code = scan_barcode(["part", "command", "stockitem"])

        # Handle command switches or exit
        if code in {"exit", "add", "subtract", "submit"}:
            if code == "exit" or code == "submit":
                print("Exiting mode")
                active = False
            else:
                print(f"Switching to {code.upper()} mode!!!")
                command = code
            continue

        # Process stock items
        stock_item_id = -1
        if item_type == "stockitem":
            stock_details = get_stock_by_id(code)
            if stock_details:
                stock_item_id = code
                code = stock_details["part"]
            else:
                print("Invalid stock item scanned.")
                continue

        # Retrieve part details
        part_details = get_part_by_id(code)
        if not part_details:
            print("The part code was not found on the server. Please try a different item.")
            continue

        # Check stock availability
        if part_details["stock_item_count"] == 0:
            print("This part is out of stock. Please try a different item.")
            continue

        # If multiple stock items exist, prompt for stock item scan
        if part_details["stock_item_count"] > 1 and stock_item_id == -1:
            print("This item has multiple stock items. Please scan the STOCK ITEM code.")

            while True:
                _, stock_code = scan_barcode(["stockitem"])
                stock_details = get_stock_by_id(stock_code)

                if not stock_details:
                    print("The stock item code was not found. Please try again.")
                    continue
                if stock_details["part"] != code:
                    print("The stock item does not belong to the selected part. Scan a matching STOCK ITEM.")
                    continue

                stock_item_id = stock_code
                break

        # Assign stock item if not already set
        if stock_item_id == -1:
            stock_item_id = next((stock["pk"] for stock in stocks if stock["part"] == code), -1)

        # Update action queue
        action = 1 if command == "add" else -1
        action_queue[stock_item_id] = [action_queue.get(stock_item_id, [0])[0] + action, code]

        print(f"{command.upper()} part {part_details['name']} (Code: {code}, Stock: {stock_item_id})")
        print("\n" * 50)
        print("===============================")
        print_action_queue()

    # Final action queue summary
    print("==========================================")
    print("WARNING: YOU ARE ABOUT TO UPDATE THE DATABASE WITH THE FOLLOWING CHANGES:")
    print_action_queue()
    print("==========================================")
    print("Submit changes? (SCAN SUBMIT CODE)")
    _, submit_code = scan_barcode(["command"])
    if submit_code == "submit":
        for stock_id, (quantity, _) in action_queue.items():
            stock_entry = next((stock for stock in stocks if stock["pk"] == stock_id), None)
            if stock_entry:
                current_quantity = stock_entry["quantity"]
                new_quantity = current_quantity + quantity
                update_stock(stock_id, new_quantity)
    else:
        print("Changes discarded. Goodbye!")



