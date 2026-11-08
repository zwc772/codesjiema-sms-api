"""Rent a US number for one service (single_service) and read its SMS.

Usage: python rental.py whatsapp 1m
Docs:  https://codesjiema.com/apidoc  (section: 号码租赁)
"""
import sys

from client import Client


def main():
    service = sys.argv[1] if len(sys.argv) > 1 else "whatsapp"
    term = sys.argv[2] if len(sys.argv) > 2 else "1m"
    api = Client()

    offers = api.get("/api/rental/offers")
    svc = next((s for s in offers["single_service"]["services"] if s["service"] == service), None)
    if not svc or not svc["in_stock"]:
        raise SystemExit("service not available for rental right now")
    plan = next((t for t in svc["terms"] if t["term"] == term and t["in_stock"]), None)
    if not plan:
        raise SystemExit("term not available")
    print(f"{svc['name']} {term}: ${plan['total']}")

    order = api.post("/api/rental/order", type="single_service", term=term, service=service,
                     expected_price=plan["total"], idempotency_key=api.new_idempotency_key())["order"]
    print("number:", order.get("number"), " order:", order["order_no"], " ends_at:", order.get("ends_at"))

    detail = api.get("/api/rental/detail", order_no=order["order_no"])
    for m in detail.get("sms", []):
        print(m["date"], m["sender"], m["text"])


if __name__ == "__main__":
    main()
