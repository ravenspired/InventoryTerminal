from Barcode import Barcode, scan_barcode

if __name__ == "__main__":
    barcode = scan_barcode()
    if barcode:
        print(f"Scanned: {barcode}")
