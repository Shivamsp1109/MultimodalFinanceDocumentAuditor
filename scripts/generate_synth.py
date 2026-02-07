import random
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


fake = Faker()


def generate_invoice(path: str, fraudulent: bool = False) -> None:
    c = canvas.Canvas(path, pagesize=letter)
    c.setFont("Helvetica", 12)

    vendor = fake.company()
    invoice_number = f"INV-{random.randint(1000,9999)}"
    date = fake.date_this_decade().isoformat()

    items = [("Item A", 2, 10.0), ("Item B", 1, 20.0)]
    subtotal = sum(q * p for _, q, p in items)
    tax = subtotal * 0.1
    total = subtotal + tax

    if fraudulent:
        total += 15  # wrong total

    c.drawString(50, 750, f"Vendor: {vendor}")
    c.drawString(50, 730, f"Invoice: {invoice_number}")
    c.drawString(50, 710, f"Date: {date}")

    y = 680
    for name, qty, price in items:
        c.drawString(50, y, f"{name} {qty} x {price}")
        y -= 20

    c.drawString(50, y - 20, f"Subtotal: {subtotal}")
    c.drawString(50, y - 40, f"Tax: {tax}")
    c.drawString(50, y - 60, f"Total: {total}")

    c.save()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--fraud", action="store_true")
    args = parser.parse_args()

    generate_invoice(args.out, fraudulent=args.fraud)
