#!/usr/bin/env bash
# CodesJiema API with cURL. export CODESJIEMA_API_KEY=... first.
# Docs: https://codesjiema.com/apidoc
set -euo pipefail
API=https://codesjiema.com
H="X-API-Key: ${CODESJIEMA_API_KEY:?set CODESJIEMA_API_KEY}"

# balance
curl -s -H "$H" "$API/api/index/user_info"

# services and countries
curl -s -H "$H" "$API/api/activation/catalog"
curl -s -H "$H" "$API/api/activation/countries?service=whatsapp"

# real-time routes and prices (no charge)
curl -s -H "$H" "$API/api/activation/quote?country=us&service=whatsapp"

# allocate a number (route from the quote above); keep the key if you retry
KEY=$(cat /proc/sys/kernel/random/uuid 2>/dev/null | tr -d - || date +%s%N)
# curl -s -H "$H" -X POST "$API/api/activation/allocate" \
#   -d country=us -d service=whatsapp -d route=ROUTE_ID -d expected_price=PRICE -d idempotency_key=$KEY

# poll SMS / cancel
# curl -s -H "$H" -X POST "$API/api/activation/poll"   -d order_no=ORDER_NO
# curl -s -H "$H" -X POST "$API/api/activation/cancel" -d order_no=ORDER_NO

# Chinese mainland numbers
curl -s -H "$H" "$API/api/cnsms/options"
curl -s -G -H "$H" "$API/api/cnsms/search" --data-urlencode "keyword=抖音"

# rental offers
curl -s -H "$H" "$API/api/rental/offers"
