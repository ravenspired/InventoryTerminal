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
_, command = scan_barcode(["command"])
if command == "exit":
    print("Quitting!")
    exit()


action_queue = []

if command == "add" or command == "subtract":
    active = True

while active:
    print("Please scan PART code. CURRENT COMMAND: ", command)
    _, item_code = scan_barcode(["part", "command"])


    if item_code == "exit":
        print("exiting mode")
        active = False
        continue

    if item_code == "add":
        print("Switching to ADD mode")
        command = "add"
        continue

    if item_code == "subtract":
        print("Switching to SUBTRACT mode")
        command = "subtract"
        continue

    item_details = get_part_from_id(item_code)
    if item_details is None:
        print("The part code was not found on the server. Please try a different item")
        continue

    if command == "add":
        print(f"Adding part {item_details["name"]} with code {item_code}")
        action_queue.push(("add", item_code))
    elif command == "subtract":
        print(f"Subtracting part {item_details["name"]} with code {item_code}")
        action_queue.push(("subtract", item_code))


    print("===============================")
    



print("Action queue: ", action_queue)
