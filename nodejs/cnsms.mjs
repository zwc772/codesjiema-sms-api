// Chinese mainland numbers (国内接码). Usage: node cnsms.mjs 抖音
import { createClient, sleep } from './client.mjs';

const keyword = process.argv[2] || '抖音';
const api = createClient();

const { rows } = await api.get('/api/cnsms/search', { keyword });
if (!rows.length) { console.log('project not found'); process.exit(1); }
const p = rows[0];

const res = await api.post('/api/cnsms/allocate', {
  project_id: p.project_id, project_name: p.name, project_token: p.token,
  ascription: '2', quantity: 1, idempotency_key: api.newKey(),
});
const order = res.orders[0];
if (order.status !== 'active') { console.log('no number', res.message); process.exit(1); }
console.log('phone', order.phone, order.province, order.carrier);

for (let i = 0; i < 240; i++) {
  await sleep(5000);
  const { order: o } = await api.post('/api/cnsms/poll', { order_no: order.order_no });
  if (o.status === 'received') {
    console.log('code', o.sms_code, '|', o.sms_content);
    await api.post('/api/cnsms/release', { order_no: order.order_no });
    process.exit(0);
  }
  if (['released', 'expired', 'failed'].includes(o.status)) { console.log('ended', o.status); process.exit(0); }
}
await api.post('/api/cnsms/release', { order_no: order.order_no });
console.log('no code, released and refunded');
