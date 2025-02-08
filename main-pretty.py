import requests
from NewBarcode import scan_barcode
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel

# InvenTree API settings
BASE_URL = "http://inventory.voronet.net/api"
API_TOKEN = "inv-d800a512df3a4c3365327b39298bcfe51782d83e-20250202"

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

console = Console()

def fetch_data(endpoint):
    """Fetch data from the InvenTree API."""
    url = f"{BASE_URL}/{endpoint}/"
    response = requests.get(url, headers=HEADERS)
    return response.json() if response.status_code == 200 else []

def get_part_by_id(part_id):
    """Retrieve a part by its ID."""
    return next((part for part in parts if part['pk'] == part_id), None)

def get_stock_by_id(stock_id):
    """Retrieve stock by its ID."""
    return next((stock for stock in stocks if stock['pk'] == stock_id), None)

def create_table():
    """Create a table to display scanned items."""
    table = Table(title="Scanned Items")
    table.add_column("Quantity", justify="center")
    table.add_column("Item Name")
    table.add_column("Item ID", justify="center")
    table.add_column("Stock ID", justify="center")
    
    for stock_id, (quantity, part_id) in action_queue.items():
        part = get_part_by_id(part_id)
        table.add_row(str(quantity), part['name'], str(part_id), str(stock_id))
    
    return table

# Fetch initial data
console.print("[bold yellow]Please wait, contacting server...[/bold yellow]")
parts = fetch_data("part")
stocks = fetch_data("stock")
console.print("[bold green]Done[/bold green]")

# Command selection
console.print("[bold cyan]Please scan COMMAND code: ADD, SUBTRACT, EXIT[/bold cyan]")
_, command = scan_barcode(["command"])

if command == "exit":
    console.print("[bold red]Quitting![/bold red]")
    exit()

action_queue = {}
active = command in {"add", "subtract"}

with Live(create_table(), refresh_per_second=2) as live:
    while active:
        console.print(f"[bold cyan]Scan PART or STOCKITEM code. CURRENT COMMAND: {command.upper()}[/bold cyan]")
        item_type, code = scan_barcode(["part", "command", "stockitem"])

        if code in {"exit", "add", "subtract"}:
            if code == "exit":
                console.print("[bold red]Exiting mode[/bold red]")
                active = False
            else:
                console.print(f"[bold magenta]Switching to {code.upper()} mode[/bold magenta]")
                command = code
            continue

        stock_item_id = -1
        if item_type == "stockitem":
            stock_details = get_stock_by_id(code)
            if stock_details:
                stock_item_id = code
                code = stock_details["part"]
            else:
                console.print(Panel("[bold red]Invalid stock item scanned![/bold red]", style="red"))
                continue

        part_details = get_part_by_id(code)
        if not part_details:
            console.print(Panel("[bold red]Part not found on the server. Try again![/bold red]", style="red"))
            continue

        if part_details["stock_item_count"] == 0:
            console.print(Panel("[bold red]This part is out of stock![/bold red]", style="red"))
            continue

        if part_details["stock_item_count"] > 1 and stock_item_id == -1:
            console.print(Panel("[bold yellow]Multiple stock items exist. Scan STOCK ITEM code![/bold yellow]", style="yellow"))
            while True:
                _, stock_code = scan_barcode(["stockitem"])
                stock_details = get_stock_by_id(stock_code)
                if not stock_details:
                    console.print("[bold red]Invalid stock item! Try again.[/bold red]")
                    continue
                if stock_details["part"] != code:
                    console.print("[bold red]Stock item does not match scanned part![/bold red]")
                    continue
                stock_item_id = stock_code
                break

        if stock_item_id == -1:
            stock_item_id = next((stock["pk"] for stock in stocks if stock["part"] == code), -1)

        action = 1 if command == "add" else -1
        action_queue[stock_item_id] = [action_queue.get(stock_item_id, [0])[0] + action, code]

        console.print(f"[bold green]{command.upper()} part {part_details['name']} (Code: {code}, Stock: {stock_item_id})[/bold green]")
        console.print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
        live.update(create_table())

console.print("[bold cyan]Final action queue:[/bold cyan]", action_queue)
