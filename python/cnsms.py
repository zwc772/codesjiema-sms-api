"""Chinese mainland numbers (国内接码): search -> allocate -> poll -> release.

Usage: python cnsms.py 抖音
Docs:  https://codesjiema.com/apidoc  (section: 国内接码)
"""
import sys
import time

from client import Client


def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "抖音"
    api = Client()

    rows = api.get("/api/cnsms/search", keyword=keyword)["rows"]
    if not rows:
        raise SystemExit("project not found")
    p = rows[0]
    print("project:", p["name"], p["project_id"])

    res = api.post("/api/cnsms/allocate", project_id=p["project_id"], project_name=p["name"],
                   project_token=p["token"], ascription="2",  # 2 = physical SIM
                   quantity=1, idempotency_key=api.new_idempotency_key())
    order = res["orders"][0]
    if order["status"] != "active":
        raise SystemExit(f"no number: {res.get('message')}")
    print("phone:", order["phone"], order.get("province"), order.get("carrier"))

    for _ in range(240):  # up to 20 minutes
        time.sleep(5)
        o = api.post("/api/cnsms/poll", order_no=order["order_no"])["order"]
        if o["status"] == "received":
            print("code:", o["sms_code"], "|", o["sms_content"])
            api.post("/api/cnsms/release", order_no=order["order_no"])
            return
        if o["status"] in ("released", "expired", "failed"):
            print("order ended:", o["status"])
            return
    api.post("/api/cnsms/release", order_no=order["order_no"])
    print("no code, released and refunded")


if __name__ == "__main__":
    main()
