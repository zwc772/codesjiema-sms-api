# CodesJiema SMS Verification API — Examples

[CodesJiema](https://codesjiema.com/) 是一个在线接码平台：用真实运营商号码接收短信验证码，支持 100+ 国家的国际接码、中国大陆手机号接码和美国号码长期租赁。

本仓库提供 **CodesJiema 开发者 API** 的调用示例（Python / Node.js / PHP / cURL），覆盖：

- 国际接码：选业务 → 选国家 → 查线路报价 → 取号 → 轮询短信 → 取消退款 / 同号再次接码
- 国内接码（中国大陆手机号）：搜索项目 → 取号 → 轮询验证码 → 释放
- 号码租赁：查询方案 → 下单 → 查看收到的短信
- 余额与订单查询

完整接口说明见官方文档：**https://codesjiema.com/apidoc**

> English: Code samples for the CodesJiema SMS-activation API — receive SMS verification codes with real phone numbers from 100+ countries, Chinese mainland numbers, and long-term US number rental. Full reference: https://codesjiema.com/apidoc

---

## 1. 获取 API 密钥

1. 在 [codesjiema.com](https://codesjiema.com/) 注册账号并充值（USDT-TRC20，1 USDT = $1）。
2. 累计已核实实付充值满 **100 USDT** 后，在 [API 文档页](https://codesjiema.com/apidoc) 顶部生成密钥。
3. 所有请求携带请求头 `X-API-Key: <你的密钥>`。

**密钥只放在环境变量或服务端配置里，不要写进代码、前端或公开仓库。** 本仓库所有示例都从环境变量 `CODESJIEMA_API_KEY` 读取。

```bash
export CODESJIEMA_API_KEY="your_developer_key"
```

## 2. 通用约定

| 项目 | 说明 |
|---|---|
| 基础地址 | `https://codesjiema.com` |
| 认证 | 请求头 `X-API-Key` |
| POST 格式 | `application/x-www-form-urlencoded` |
| 金额 | 美元（USD），与网页价格一致 |
| 返回结构 | `{"code":1,"msg":"...","time":"...","data":{...}}`，`code=1` 成功，`code=0` 业务失败（看 `msg`） |
| HTTP 状态 | 401 密钥无效；403 未满足开通条件；429 请求过于频繁（按 `Retry-After` 等待） |

**幂等（防重复扣费）**：会扣费的接口（`allocate`、`again`、`rental/order`、`cnsms/allocate`）必须带 16–64 位的 `idempotency_key`。网络超时后**用同一个 key 重试**会返回原订单，不会重复扣费。

## 3. 国际接码流程

```
GET  /api/activation/catalog            业务列表
GET  /api/activation/countries?service= 提供该业务的国家
GET  /api/activation/quote              实时线路与价格（不扣费）
POST /api/activation/allocate           取号（预扣余额）
POST /api/activation/poll               每 5 秒查询短信
POST /api/activation/cancel             未收到短信时取消退款
GET  /api/activation/again_quote → POST /api/activation/again   同号再次接码
```

有效期内没有收到短信会自动退款。

## 4. 国内接码流程（中国大陆手机号）

```
GET  /api/cnsms/options   单价、省份与运营商代码
GET  /api/cnsms/search    按关键词搜索项目（如 微信、抖音、淘宝）
POST /api/cnsms/allocate  取号（$1 / 个）
POST /api/cnsms/poll      每 5 秒查询验证码
POST /api/cnsms/release   释放号码（未收到验证码时退款）
```

取号后 20 分钟内未收到验证码会自动释放并退款。

## 5. 示例目录

| 目录 | 内容 |
|---|---|
| [`python/`](python/) | `activation.py` 国际接码完整流程；`cnsms.py` 国内接码；`rental.py` 号码租赁 |
| [`nodejs/`](nodejs/) | `activation.mjs`、`cnsms.mjs`（Node.js 18+，无第三方依赖） |
| [`php/`](php/) | `activation.php`（cURL 扩展） |
| [`curl/`](curl/) | `examples.sh` 常用接口的 cURL 命令 |

运行示例：

```bash
# Python 3.8+
pip install requests
python python/activation.py --service whatsapp --country us

# Node.js 18+
node nodejs/activation.mjs whatsapp us

# PHP 7.4+
php php/activation.php whatsapp us
```

## 6. 使用须知

- 临时号码在订单结束后会回收，只适合一次性短信验证；需要长期登录、找回密码或绑定支付的账号，请使用自己可长期掌握的号码。
- 请遵守目标平台的服务条款和当地法律法规。
- 同一 IP 每分钟最多约 120 次查询、30 次下单。

## 相关链接

- 官网：https://codesjiema.com/
- API 文档：https://codesjiema.com/apidoc
- 国内接码：https://codesjiema.com/cn
- 号码租赁：https://codesjiema.com/tel
- 使用指南与博客：https://codesjiema.com/blog

## License

MIT
