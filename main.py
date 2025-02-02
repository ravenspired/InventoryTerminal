import requests

# InvenTree API settings
BASE_URL = "http://inventory.local/api"
API_TOKEN = "inv-d800a512df3a4c3365327b39298bcfe51782d83e-20250202"

# Headers for authentication
HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}


def get_stock_count(part_id):
    """Fetch and sum stock quantities for a given part ID."""
    url = f"{BASE_URL}/stock/?part={part_id}"
    response = requests.get(url, headers=HEADERS)
    print(response)
    if response.status_code == 200:
        stock_entries = response.json()
        print(stock_entries)
        return sum(entry["quantity"] for entry in stock_entries)  # Sum all stock entries
    return 0

# Example usage
part_name = "dummy item"
# part_id = get_part_id(part_name)
part_id = eval(input("Scan Barcode: ")).get("part", "The key 'part' was not found in the dictionary.")

if part_id:
    stock_count = get_stock_count(part_id)
    print(f"Total stock count for '{part_name}': {stock_count}")
else:
    print(f"Part '{part_name}' not found.")

