<?php
// International SMS activation with PHP cURL. Usage: php activation.php whatsapp us
// Docs: https://codesjiema.com/apidoc

$apiKey = getenv('CODESJIEMA_API_KEY') ?: exit("Set CODESJIEMA_API_KEY\n");
$service = $argv[1] ?? 'whatsapp';
$country = $argv[2] ?? 'us';

function cj(string $method, string $path, array $params = []): array
{
    global $apiKey;
    $url = 'https://codesjiema.com' . $path;
    $ch = curl_init();
    if ($method === 'GET') {
        $url .= $params ? '?' . http_build_query($params) : '';
    } else {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
    }
    curl_setopt_array($ch, [
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT => 45,
        CURLOPT_HTTPHEADER => ['X-API-Key: ' . $apiKey],
    ]);
    $raw = curl_exec($ch);
    $status = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    $body = json_decode((string) $raw, true);
    if ($status !== 200 || !is_array($body) || (int) ($body['code'] ?? 0) !== 1) {
        throw new RuntimeException("HTTP $status: " . ($body['msg'] ?? 'request failed'));
    }
    return $body['data'] ?? [];
}

$quote = cj('GET', '/api/activation/quote', ['country' => $country, 'service' => $service]);
$route = $quote['routes'][0] ?? null;
if (!$route) exit("No numbers right now, try another country\n");
echo "route {$route['route']} price \${$route['price']}\n";

$order = cj('POST', '/api/activation/allocate', [
    'country' => $country,
    'service' => $service,
    'route' => $route['route'],
    'expected_price' => $route['price'],
    'idempotency_key' => bin2hex(random_bytes(16)),
])['order'];
if ($order['status'] !== 'active') exit("status {$order['status']}\n");
echo "phone {$order['phone']}  order {$order['order_no']}\n";

for ($i = 0; $i < 120; $i++) {
    sleep(5);
    $o = cj('POST', '/api/activation/poll', ['order_no' => $order['order_no']])['order'];
    if (!empty($o['sms'])) {
        foreach ($o['sms'] as $m) echo "SMS {$m['sender']}: {$m['text']} (code {$m['code']})\n";
        exit(0);
    }
    if (in_array($o['status'], ['cancelled', 'failed', 'finished'], true)) exit("ended {$o['status']}\n");
}
cj('POST', '/api/activation/cancel', ['order_no' => $order['order_no']]);
echo "No SMS, cancelled and refunded\n";
