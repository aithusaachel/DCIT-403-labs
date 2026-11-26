
import csv
from datetime import date, timedelta
from pathlib import Path

from mcp.server.fastmcp import FastMCP  

DATA = Path(__file__).resolve().parent / "data" / "pharmacy_stock.csv"
mcp = FastMCP("pharmacy")




def _load() -> list[dict]:
    with open(DATA, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _save(rows: list[dict]) -> None:
    with open(DATA, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _find(rows: list[dict], item: str, strength: str) -> dict | None:
    item, strength = item.lower().strip(), strength.lower().replace(" ", "")
    for r in rows:
        if r["item"].lower() == item and r["strength"].lower().replace(" ", "") == strength:
            return r
    return None


def _view(r: dict) -> dict:
    days_left = (date.fromisoformat(r["expiry_date"]) - date.today()).days
    return {"item": r["item"], "strength": r["strength"], "form": r["form"],
            "quantity": int(r["quantity"]), "unit_price_ghs": float(r["unit_price_ghs"]),
            "expiry_date": r["expiry_date"], "days_to_expiry": days_left}





@mcp.tool()
def search_stock(name: str) -> list[dict]:
    """Find medicines whose name contains `name` (case-insensitive, e.g. 'amox').
    Returns item, strength, form, quantity, unit price (GHS) and expiry for every match.
    Use this first when the exact item name or strength is not known."""
    hits = [_view(r) for r in _load() if name.lower().strip() in r["item"].lower()]
    return hits or [{"message": f"No medicine matching '{name}' is stocked."}]


@mcp.tool()
def check_quantity(item: str, strength: str) -> dict:
    """Return how many units of one product are in stock.
    A product is an item plus a strength, e.g. item='Amoxicillin', strength='500mg'."""
    r = _find(_load(), item, strength)
    if not r:
        return {"error": f"No product '{item} {strength}'. Use search_stock to see what exists."}
    return {"item": r["item"], "strength": r["strength"], "quantity": int(r["quantity"])}


@mcp.tool()
def expiring_within(days: int = 60) -> list[dict]:
    """List products that expire within the next `days` days (default 60), soonest first.
    Already-expired products are included with a negative days_to_expiry."""
    if days < 0:
        return [{"error": "days must be 0 or more."}]
    limit = date.today() + timedelta(days=days)
    soon = [_view(r) for r in _load() if date.fromisoformat(r["expiry_date"]) <= limit]
    soon.sort(key=lambda v: v["expiry_date"])
    return soon or [{"message": f"Nothing expires in the next {days} days."}]


@mcp.tool()
def record_sale(item: str, strength: str, quantity: int) -> dict:
    """Record a sale of `quantity` units of one product (item + strength) and reduce the stock.
    Refuses if the quantity is not positive, the product does not exist, it has expired,
    or there is not enough stock. Returns the total price in GHS and the units remaining."""
    if quantity <= 0:
        return {"ok": False, "error": "Quantity must be at least 1."}
    rows = _load()
    r = _find(rows, item, strength)
    if not r:
        return {"ok": False, "error": f"No product '{item} {strength}'. Use search_stock first."}
    if date.fromisoformat(r["expiry_date"]) < date.today():
        return {"ok": False, "error": f"{r['item']} {r['strength']} expired on {r['expiry_date']}. Do not sell."}
    in_stock = int(r["quantity"])
    if quantity > in_stock: 
        return {"ok": False, "error": f"Only {in_stock} in stock; cannot sell {quantity}."}
    r["quantity"] = str(in_stock - quantity)
    _save(rows)
    return {"ok": True, "item": r["item"], "strength": r["strength"], "sold": quantity,
            "total_ghs": round(quantity * float(r["unit_price_ghs"]), 2),
            "remaining": in_stock - quantity}




@mcp.resource("stock://inventory")
def inventory() -> str:
    """The full pharmacy stock list as CSV text (read-only)."""
    return DATA.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run() 
