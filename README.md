# Vobiz — One-Way Number Masking

**Give every person you want to protect their own dedicated
[Vobiz](https://vobiz.ai) masking number that forwards to them, hiding both the
caller and the destination — the simplest masking setup, where *anyone* can dial
in from *any* phone.**

Each masking number maps one-to-one to a real destination. When anybody dials it,
Vobiz calls your `answer_url`; your backend looks up the destination (by the
dialled number alone — the caller is irrelevant) and bridges, showing the masking
number as the caller ID.

> Built and maintained by **Team Vobiz**. This is the "one-way (destination-based)"
> flavour of Vobiz number masking.

---

## How it works

```
any caller ──dial M1──► Vobiz ──POST /answer {To=M1}──► your backend
                                                        └─ look up M1 -> destination
any caller ◄══ bridged ══ Vobiz ◄── <Dial callerId=M1><Number>destination</> ──┘
                           └─ call destination AS M1 ─► destination rings (sees M1)
```

The caller's number (`From`) is **ignored**, so registered *and* non-registered
callers work. The destination only ever sees the masking number.

> **Numbers needed: one per destination** — the masking number *is* the address.
> This is the most flexible setup for callers but the most number-hungry.

---

## Configuration (everything via `.env`)

```bash
cp .env.example .env
```

```ini
VOBIZ_AUTH_ID=MA_XXXXXXXXXXXXXXXX
VOBIZ_AUTH_TOKEN=your_auth_token
VOBIZ_API_BASE=https://api.vobiz.ai/api/v1
PUBLIC_BASE_URL=https://your-tunnel.trycloudflare.com

# masking:destination pairs (E.164, no '+'), comma-separated
ONE_WAY_MAPPINGS=919000000001:919876511111,919000000002:919876522222
```

`.env` is gitignored; placeholder defaults let the app and tests run without one.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app:app --reload --port 8003
```

### Test offline

```bash
pytest -q
# any caller dialling a masking number reaches its destination:
curl -s -X POST localhost:8003/answer -d "From=910000000000" -d "To=919000000001"
# -> <Dial callerId="919000000001"><Number>919876511111</Number></Dial>
```

### Go live

```bash
uvicorn app:app --port 8003
cloudflared tunnel --url http://127.0.0.1:8003    # put URL in .env as PUBLIC_BASE_URL
./.venv/bin/python setup_live.py                  # create app + attach masking numbers
```

`setup_live.py` calls **Create Application** and **Attach** for every masking
number in `ONE_WAY_MAPPINGS`.

---

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | FastAPI `/answer` webhook (+ `/health`). |
| `mappings.py` | masking→destination map, loaded from `.env`. |
| `vobiz_xml.py` | Vobiz XML builders. |
| `setup_live.py` | Create Application + attach masking numbers. |
| `test_flows.py` | Offline tests (any-source reach, unknown-number reject). |
| `GUIDE.md` | Beginner-friendly deep dive. |

---

## Architecture

- **Vobiz** owns the numbers, terminates the call, and bridges; it asks your
  backend on every call.
- **Your backend** holds the (tiny) masking→destination map and is stateless per
  request.
- One number = one destination, always; there is no reuse.

For production: store the map in a database, verify requests come from Vobiz, and
use a stable HTTPS domain.

---

## Pros & cons

**Pros**
- Most flexible for callers — any source number works (registered or not).
- Dead simple — no sessions, no PIN, no caller checks.
- Easy mental model — one number per person, like a forwarding number.

**Cons**
- Most expensive in numbers — one DID per destination.
- No caller restriction by default — anyone with the number reaches the destination.

---

## Built by Team Vobiz

[Vobiz](https://vobiz.ai) is a programmable voice & SIP-trunking platform.

Author: **Piyush Sahoo** — [LinkedIn](https://www.linkedin.com/in/piyush-s713/)

## License

[MIT](./LICENSE) © Vobiz
