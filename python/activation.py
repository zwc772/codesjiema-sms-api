"""International SMS activation: quote -> allocate -> poll -> (cancel).

Usage: python activation.py --service whatsapp --country us
Docs:  https://codesjiema.com/apidoc
"""
import argparse
import time

from client import Client, CodesJiemaError


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--service", required=True, help="service id from /api/activation/catalog, e.g. whatsapp")
    ap.add_argument("--country", required=True, help="ISO country code, e.g. us, gb")
    ap.add_argument("--max-price", type=float, help="highest price you accept (USD)")
    ap.add_argument("--wait", type=int, default=600, help="seconds to wait for SMS")
    a = ap.parse_args()

    api = Client()
    print("balance: $", api.get("/api/index/user_info")["money"])

    quote = api.get("/api/activation/quote", country=a.country, service=a.service)
    routes = quote.get("routes") or []
    if not routes:
        raise SystemExit("no numbers for this country/service right now, try another country")
    route = routes[0]  # cheapest
    print(f"route {route['route']}  price ${route['price']}  multi_sms={route['multi_sms']}")
    if a.max_price is not None and float(route["price"]) > a.max_price:
        raise SystemExit("cheapest route is above --max-price")

    key = api.new_idempotency_key()
    try:
        order = api.post("/api/activation/allocate", country=a.country, service=a.service,
                          route=route["route"], expected_price=route["price"], idempotency_key=key)["order"]
    except CodesJiemaError as e:
        raise SystemExit(f"allocate failed: {e}")
    if order["status"] != "active":
        raise SystemExit(f"order {order['order_no']} status={order['status']}")
    print("phone:", order["phone"], " order:", order["order_no"])

    deadline = time.time() + a.wait
    while time.time() < deadline:
        time.sleep(5)
        o = api.post("/api/activation/poll", order_no=order["order_no"])["order"]
        if o.get("sms"):
            for m in o["sms"]:
                print(f"SMS from {m.get('sender')}: {m.get('text')}  code={m.get('code')}")
            return
        if o["status"] in ("cancelled", "failed", "finished"):
            print("order ended:", o["status"])
            return
    api.post("/api/activation/cancel", order_no=order["order_no"])
    print("no SMS received, order cancelled and refunded")


if __name__ == "__main__":
    main()
