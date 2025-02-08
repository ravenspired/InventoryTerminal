import requests
from NewBarcode import scan_barcode
from Stack import Stack
from tqdm import tqdm


def run():
    # InvenTree API settings
    BASE_URL = "http://inventory.local/api"
    print("Scan your ID card")
    _,API_TOKEN = scan_barcode(["api"]) # Use PDF417 barcode type

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


    def update_stock(stock_entry_id, new_quantity, new_location=-1):
        """Update stock quantity for a specific stock entry."""
        url = f"{BASE_URL}/stock/{stock_entry_id}/"
        if new_location != -1:
            payload = {"quantity": new_quantity, "location": new_location}
        else:
            payload = {"quantity": new_quantity}
        
        response = requests.patch(url, json=payload, headers=HEADERS)
        
        if response.status_code in [200, 204]:  # 200 OK or 204 No Content
            #print(f"Stock updated successfully: ID {stock_entry_id}, New Quantity: {new_quantity}")
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
        print("Quantity | Item Name | Item ID | Stock ID | Location")
        print("-------------------------------------------")
        for stock_id, (quantity, part_id, location) in action_queue.items():
            part = get_part_by_id(part_id)
            print(f"{quantity} | {part['name']} | {part_id} | {stock_id} | {location if location_mode else 'N/A'}")
        print("\n")




    # Fetch initial data
    print("Please wait, contacting server...")
    parts = fetch_data("part")
    stocks = fetch_data("stock")
    print("Done")


    action_queue = {}
    active = True
    command = "subtract"
    first_scan = True
    second_scan = False
    location_mode = False
    location = None
    previous_stock = None
    use_prev_stock_item = False
    repeat = 1

    while active:
        print(f"Please scan PART or STOCKITEM code. CURRENT COMMAND: {command}")
        item_type, code = scan_barcode(["part", "command", "stockitem", "stocklocation"])

        # Handle command switches or exit


        if first_scan:
            if code == "location":
                print("Switching to location mode.")
                location_mode = True
                command = "location"
                first_scan = False
                second_scan = True
                print("Please scan the location code. To set the location to none, begin scanning your items.")
                continue

        if second_scan:
            if item_type == "stocklocation":
                location = code
                print(f"Location set to {location}.")
                print("Please begin scanning your items.")
                second_scan = False
                continue


        if code in {"exit", "add", "subtract", "submit", "location"}:
            if code == "exit" or code == "submit":
                print("Exiting mode")
                active = False
            if code == "location":
                print("Please finish the current transaction before switching to location mode.")
                continue
            else:
                print(f"Switching to {code.upper()} mode!!!")
                command = code
            continue

        if code in {"repeat5", "repeat10", "repeat20"}:
            if previous_stock is None:
                print("No previous stock item to repeat. You can only use this code after scanning an item.")
                continue
            print(f"You scanned a repeat code. Repeating the last scan, {int(code[6:])} times.")
            repeat = int(code[6:])
            use_prev_stock_item = True

        if item_type == "stocklocation":
            print("This is a location code. Please scan a part or stock item code.")

        

        
                

        # Process stock items
        stock_item_id = -1
        if use_prev_stock_item:
            code = previous_stock


        if item_type == "stockitem" or use_prev_stock_item:
            stock_details = get_stock_by_id(code)
            if stock_details:
                stock_item_id = code
                code = stock_details["part"]
            else:
                print("Invalid stock item scanned.")
                continue


        # Retrieve part details
        part_details = get_part_by_id(code)

        if not use_prev_stock_item:
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
            if use_prev_stock_item:
                stock_item_id = previous_stock
                use_prev_stock_item = False
            else:
                stock_item_id = next((stock["pk"] for stock in stocks if stock["part"] == code), -1)

        # Update action queue


        previous_stock = stock_item_id
        

        if not location_mode:
            action = repeat if command == "add" else -1 * repeat
            action_queue[stock_item_id] = [action_queue.get(stock_item_id, [0])[0] + action, code, "N/A"]
        else:
            action_queue[stock_item_id] = [action_queue.get(stock_item_id, [0])[0], code, location]

        use_prev_stock_item = False # Reset flag
        repeat = 1 # Reset repeat count

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
        print("Submitting changes... This may take a while. Do not terminate the program.")
        for stock_id, (quantity, location, _) in tqdm(action_queue.items()):
            stock_entry = next((stock for stock in stocks if stock["pk"] == stock_id), None)
            if stock_entry:
                current_quantity = stock_entry["quantity"]
                new_quantity = current_quantity + quantity
                if location_mode:
                    new_location = action_queue[stock_id][2]
                    update_stock(stock_id, new_quantity, new_location)
                else:
                    update_stock(stock_id, new_quantity)
        print("Changes submitted successfully. Goodbye!")
    else:
        print("Changes discarded. Goodbye!")



