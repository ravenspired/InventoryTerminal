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


parts = update_parts()

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