// International SMS activation. Usage: node activation.mjs whatsapp us
import { createClient, sleep } from './client.mjs';

const [service = 'whatsapp', country = 'us'] = process.argv.slice(2);
const api = createClient();

const quote = await api.get('/api/activation/quote', { country, service });
const route = (quote.routes || [])[0];
if (!route) { console.log('no numbers right now, try another country'); process.exit(1); }
console.log(`route ${route.route} price $${route.price}`);

const { order } = await api.post('/api/activation/allocate', {
  country, service, route: route.route, expected_price: route.price, idempotency_key: api.newKey(),
});
if (order.status !== 'active') { console.log('status', order.status); process.exit(1); }
console.log('phone', order.phone, 'order', order.order_no);

for (let i = 0; i < 120; i++) {
  await sleep(5000);
  const { order: o } = await api.post('/api/activation/poll', { order_no: order.order_no });
  if (o.sms && o.sms.length) {
    o.sms.forEach((m) => console.log(`SMS ${m.sender}: ${m.text} (code ${m.code})`));
    process.exit(0);
  }
  if (['cancelled', 'failed', 'finished'].includes(o.status)) { console.log('ended', o.status); process.exit(0); }
}
await api.post('/api/activation/cancel', { order_no: order.order_no });
console.log('no SMS, cancelled and refunded');
