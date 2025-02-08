import requests
from NewBarcode import scan_barcode
from Stack import Stack

# InvenTree API settings
BASE_URL = "http://inventory.voronet.net/api"
API_TOKEN = "inv-d800a512df3a4c3365327b39298bcfe51782d83e-20250202"

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def update_parts():
    """Fetch all part entries"""
    url = f"{BASE_URL}/part/"
    response = requests.get(url, headers=HEADERS)
    print(response)
    if response.status_code == 200:
        parts = response.json()
        print(parts)
        return parts  # Return all part entries
    return []

def update_stock():
    """Fetch all stock entries"""
    url = f"{BASE_URL}/stock/"
    response = requests.get(url, headers=HEADERS)
    print(response)
    if response.status_code == 200:
        stock = response.json()
        print(stock)
        return stock  # Return all stock entries
    return []

def get_part_from_id(part_id):
    for part in parts:
        if part['pk'] == part_id:
            return part
    return None

def get_stock_from_id(stock_id):
    for stock in stocks:
        if stock['pk'] == stock_id:
            return stock
    return None

print("Please wait, contacting server...")
parts = update_parts()
stocks = update_stock()
print("Done")
print("Please scan COMMAND code. ADD, SUBTRACT, EXIT")
_, command = scan_barcode(["command"])
if command == "exit":
    print("Quitting!")
    exit()


action_queue = {}

if command == "add" or command == "subtract":
    active = True

while active:
    print("Please scan PART or STOCKITEM code. CURRENT COMMAND: ", command)
    type, code = scan_barcode(["part", "command", "stockitem"])
    stock_item = -1


    if code == "exit":
        print("exiting mode")
        active = False
        continue

    if code == "add":
        print("Switching to ADD mode")
        command = "add"
        continue

    if code == "subtract":
        print("Switching to SUBTRACT mode")
        command = "subtract"
        continue

    if type == "stockitem":
        print("Scanned stock item")
        stock_details = get_stock_from_id(code)
        stock_item = code
        print(stock_item)
        code = stock_details["part"]
        


    item_details = get_part_from_id(code)
    if item_details is None:
        print("The part code was not found on the server. Please try a different item")
        continue

    if item_details["stock_item_count"] == 0:
        print("This part is out of stock. Please try a different item")
        continue

    if item_details["stock_item_count"] >> 1 and stock_item == -1:
        print("This item has more than one stock item. Please scan the STOCK ITEM code. The label doesn't have text.")
        finished_getting_stock = False
        while not finished_getting_stock:

            _, stock_item_code = scan_barcode(["stockitem"])
            stock_details = get_stock_from_id(stock_item_code)
            if stock_details is None:
                print("The stock item code was not found on the server. Please try a different code")
                continue
            if stock_details["part"] != code:
                print("The stock item does not belong to the selected part. Please scan a STOCK ITEM on the same packaging as the part")
                continue
            stock_item = stock_item_code
            finished_getting_stock = True
    if stock_item == -1:
        for stock in stocks:
            if stock["part"] == code:
                stock_item = stock["pk"]
                break


    if command == "add":
        print(f"Adding part {item_details["name"]} with code {code} and stock code {stock_item}")
        action_queue[stock_item] = [action_queue.get(stock_item, [0])[0] + 1, code]
    elif command == "subtract":
        print(f"Subtracting part {item_details["name"]} with code {code} and stock code {stock_item}")
        action_queue[stock_item] = [action_queue.get(stock_item, [0])[0] - 1, code]


    print("===============================")
    


    



print("Action queue: ", action_queue)
