import requests
from NewBarcode import scan_barcode
from Stack import Stack

# InvenTree API settings
BASE_URL = "http://inventory.local/api"
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
        return parts  # Return all stock entries
    return []

def get_part_from_id(part_id):
    for part in parts:
        if part['pk'] == part_id:
            return part
    return None

print("Please wait, contacting server...")
parts = update_parts()
print("Done")
print("Please scan COMMAND code. ADD, SUBTRACT, EXIT")
_, command = scan_barcode(["cmd"])
if command == "exit":
    print("Quitting!")
    exit()


action_queue = Stack()

if command == "add" or command == "subtract":
    active = True

while active:
    print("Please scan PART code")
    _, item_code = scan_barcode(["part", "cmd"])


    if item_code == "exit":
        print("exiting mode")
        active = False
        continue

    item_details = get_part_from_id(item_code)
    if item_details is None:
        print("The part code was not found on the server. Please try a different item")
        continue

    if command == "add":
        print(f"Adding part {item_details["name"]} with code {item_code}")
        action_queue.append(("add", item_code))
    elif command == "subtract":
        print(f"Subtracting part {item_details["name"]} with code {item_code}")
        action_queue.append(("subtract", item_code))


print("Action queue: ", action_queue)

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


print("Part ID:", part_id)
if part_id:
    for part in parts:
        if part['pk'] == int(part_id):
            print(part)
            print("found")
            break