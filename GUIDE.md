# Strategy 3 — One-Way Masking (Destination Based): The Complete Beginner Guide

> Read Strategy 1's guide first if you are brand new — it explains masking number,
> Answer URL, `<Dial>`, and bridging. This guide assumes you know those four words
> and focuses on what makes **one-way** mapping special: it is the **simplest** to
> reason about, the **most flexible** for callers, and the **most expensive** in
> phone numbers. We explain exactly why, slowly.

---

## Table of contents

1. [What "one-way" means (and why the name is a little misleading)](#1-what-one-way-means)
2. [The single big idea: one number per destination](#2-the-single-big-idea)
3. [The cast and numbers](#3-the-cast-and-numbers)
4. [How many phone numbers do you need? (the expensive truth)](#4-how-many-numbers-do-you-need)
5. [The end-to-end story](#5-the-end-to-end-story)
6. [Pictures of the flow](#6-pictures-of-the-flow)
7. [The exact messages on the wire](#7-the-exact-messages-on-the-wire)
8. [The code, line by line](#8-the-code-line-by-line)
9. [How to run it](#9-how-to-run-it)
10. [Connecting to your real Vobiz number](#10-connecting-to-your-real-vobiz-number)
11. [Testing without real calls](#11-testing-without-real-calls)
12. [What can go wrong](#12-what-can-go-wrong)
13. [Pros, cons, and when to choose this](#13-pros-cons-and-when-to-choose-this)
14. [FAQ](#14-faq)
15. [Glossary](#15-glossary)

---

## 1. What "one-way" means

The name "one-way" does **not** mean only one person can talk. Both people still
have a two-way *conversation* once connected. "One-way" refers to how the
**mapping** is decided:

> The destination is decided **only** by *which masking number was dialled*. The
> system does **not** care *who* is calling.

Compare with the two-way strategies, where the system had to check *who* the
caller was to pick the right direction. Here, there is no direction-guessing at
all. Each masking number has exactly **one** meaning: "calls to this number go to
*this one* real person." Always. No matter who dials.

Think of it like a **redirect / forwarding number**. You give out a special
number, and *anyone* who calls it gets forwarded to the same real destination,
with the real destination's number hidden behind the masking number.

---

## 2. The single big idea: one number per destination

Here is the entire strategy in one sentence:

> **Give every person you want to protect their own personal masking number, and
> forward that number to them — showing the masking number as the caller ID.**

So:

- Destination D1 (`919876511111`) gets masking number M1 (`918050001001`).
- Destination D2 (`919876522222`) gets masking number M2 (`918050001002`).
- Destination D3 (`919876533333`) gets masking number M3 (`918050001003`).

When **anybody** dials M1, they reach D1. When anybody dials M2, they reach D2.
The caller's own number is irrelevant — that is why **the caller can be a
non-registered, unknown number**. This is the most flexible setup for callers:
your agent can call from any phone, the customer can call from any phone, even a
borrowed one, and it still works.

---

## 3. The cast and numbers

```
Destination D1 (e.g. agent)    real: +91 98765 11111   (code: 919876511111)
Destination D2 (e.g. customer) real: +91 98765 22222   (code: 919876522222)
Destination D3 (e.g. support)  real: +91 98765 33333   (code: 919876533333)

Masking numbers (one per destination):
  M1 -> D1   +91 80 5000 1001   (code: 918050001001)
  M2 -> D2   +91 80 5000 1002   (code: 918050001002)
  M3 -> D3   +91 80 5000 1003   (code: 918050001003)
```

> Your real Vobiz number `+91 90000 00001` can be the masking number for **one**
> destination. To protect two people one-way, you need two numbers; for three
> people, three numbers; and so on. That is the trade-off of this strategy (see
> next section).

---

## 4. How many numbers do you need?

The honest answer, and the main downside:

> **One masking number for every destination you want to reach.**

If you want callers to be able to reach 100 different protected people one-way,
you need **100 masking numbers**. There is no reuse trick here, because the number
*is* the address of the person. Two people cannot share one number, or dialling it
would be ambiguous.

This makes one-way mapping the **most expensive** strategy in terms of phone
numbers — you pay rent for each DID. Compare:

| Strategy | Numbers needed |
|----------|----------------|
| 1 — two-way client-hosted | 2 per pair (or 2 reused across pairs with caller-keying) |
| 2 — two-way session | a small pool sized to peak concurrency |
| **3 — one-way** | **one per destination (the most)** |
| 4 — PIN based | exactly 1 total |

So why ever choose one-way? Because it buys you **simplicity** and **caller
freedom**: no session bookkeeping, no "registered numbers only" restriction, no
PIN entry. If you only need to protect a handful of destinations and want the
easiest possible setup where *anyone* can call in, one-way is delightful.

---

## 5. The end-to-end story

1. You decide to protect the agent (`919876511111`). You assign them a personal
   masking number **M1** (`918050001001`) and put a row in your table:
   `M1 → 919876511111`.
2. You hand out M1 wherever the agent's number would normally appear — on a
   delivery slip, in an SMS, in the app: "Call your agent at +91 80 5000 1001."
3. A customer (from **any** phone, registered or not) dials **M1**.
4. The call reaches Vobiz (owner of M1). Vobiz asks your **Answer URL**: "someone
   dialled M1, what do I do?" It also tells you who called, but **you ignore that
   part** — one-way doesn't care who calls.
5. Your server looks up M1 in its table, finds `919876511111`, and replies:
   `<Dial callerId="918050001001"><Number>919876511111</Number></Dial>`.
6. Vobiz calls the agent's real number, showing **M1** as the caller ID, and
   bridges the two calls. They talk. The customer never saw the agent's real
   number; the agent saw M1, not the customer's real number (because the inbound
   leg presents the masking number).

That's the whole life cycle. No sessions, no expiry, no PIN. The mapping just sits
there and forwards.

---

## 6. Pictures of the flow

```
  Any caller            Vobiz (owns M1)            Your server            Destination D1
   (any number)              |                          |                  919876511111
       |                     |                          |                       |
   1.  |  dial M1 (918050001001)                        |                       |
       |-------------------->|                          |                       |
   2.  |                     |  POST /answer            |                       |
       |                     |  From=ANYTHING  To=M1    |                       |
       |                     |------------------------->|                       |
   3.  |                     |        look up M1 -> 919876511111 (ignore From)  |
       |                     |  <Dial callerId=M1>      |                       |
       |                     |    <Number>919876511111</Number></Dial>         |
       |                     |<-------------------------|                       |
   4.  |                     |  call D1 AS M1                                    |
       |                     |------------------------------------------------>|
   5.  |                     |                          |       D1 answers (sees M1)
       |                     |<------------------------------------------------|
   6.  |==================== BRIDGED: caller <-> M1 <-> D1 ====================|
```

The key visual difference from two-way: notice **`From=ANYTHING`** — the caller's
identity does not affect the lookup at all.

---

## 7. The exact messages on the wire

### Vobiz → your Answer URL

Same form POST as always:

```
From=<any number>&To=918050001001&CallUUID=xyz&Direction=inbound&CallStatus=ringing
```

We only use `To` (the masking number). We deliberately **ignore `From`**.

### Your reply (valid number)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Dial callerId="918050001001" timeout="30">
    <Number>919876511111</Number>
  </Dial>
</Response>
```

### Your reply (unknown masking number)

If someone dials a masking number you have no row for:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Speak>This masking number is not in service.</Speak>
  <Hangup reason="unknown_number"/>
</Response>
```

---

## 8. The code, line by line

This is the simplest of the four strategies. Two tiny files.

### `mappings.py`

```python
MAPPINGS = {
    "918050001001": "919876511111",  # M1 -> D1
    "918050001002": "919876522222",  # M2 -> D2
    "918050001003": "919876533333",  # M3 -> D3
}

def resolve(masking_number):
    return MAPPINGS.get(masking_number)   # destination, or None if unknown
```

That's the whole brain: a dictionary from masking number to destination, and a
one-line lookup. Notice `resolve` takes **only** the masking number — no caller
argument, because one-way doesn't use it.

### `app.py`

```python
@app.post("/answer")
async def answer(From=Form(...), To=Form(...), ...):
    destination = mappings.resolve(To)         # look up by dialled number only
    if destination is None:
        return Response(response(speak("This masking number is not in service."),
                                 hangup(reason="unknown_number")), media_type=XML)

    # Source number (From) is intentionally ignored — any caller is allowed.
    return Response(response(dial(destination, caller_id=To, timeout=30)),
                    media_type=XML)
```

We accept `From` (Vobiz always sends it) but never use it. We look up `To`, and if
we know it, we dial the destination using `To` itself as the caller ID. Done.

> Notice `caller_id=To`: the masking number that was dialled becomes the caller ID
> shown to the destination. So even though the call physically comes from a
> stranger, the destination sees the friendly masking number.

---

## 9. How to run it

```bash
cd "number-masking-python"
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd 3_one_way
uvicorn app:app --reload --port 8003
```

---

## 10. Connecting to your real Vobiz number

1. In `mappings.py`, map your real number to the destination you want it to
   forward to, e.g. `"919000000001": "919876511111"` (calls to your Vobiz number
   reach the agent, hiding the agent's number).
2. Start the server; in a second terminal: `ngrok http 8003`.
3. In the Vobiz dashboard, set the Answer URL of `+91 90000 00001` to
   `https://<your-ngrok>.ngrok-free.app/answer` (POST).
4. Call `+91 90000 00001` from **any** phone — you will be forwarded to the
   destination, and the destination will see your Vobiz number, not your real one.

Because one-way needs one number per destination, your single number can protect
exactly **one** destination at a time in a live demo. To protect more people,
rent more numbers.

---

## 11. Testing without real calls

```bash
python - <<'PY'
import requests
# any caller -> M1 reaches D1
print(requests.post("http://localhost:8003/answer",
      data={"From":"910000000000","To":"918050001001"}).text)
# unknown masking number -> hangup
print(requests.post("http://localhost:8003/answer",
      data={"From":"910000000000","To":"910000000099"}).text)
PY
```

Automated tests confirm that two different (unregistered) callers both reach the
mapped destination, and that unknown numbers are rejected:

```bash
pytest -q
```

---

## 12. What can go wrong

| Symptom | Cause | Fix |
|---------|-------|-----|
| "Not in service" message | The dialled number has no row in `MAPPINGS` | Add the masking→destination row |
| Destination sees the real caller's number | You set `callerId` wrong | Use `caller_id=To` (the masking number) |
| You ran out of budget for numbers | One-way needs one DID per destination | Switch to PIN (Strategy 4) or session (Strategy 2) |
| Anyone can reach the destination | That's by design (any caller allowed) | If you need restriction, use Strategy 1 or add a check |

---

## 13. Pros, cons, and when to choose this

**Pros**
- **Most flexible for callers** — any source number works (registered or not).
- **Dead simple** — no sessions, no PIN, no caller checks. Easiest to build and
  debug.
- **Easy mental model** — one number = one person, like a forwarding number.

**Cons**
- **Most expensive in numbers** — one DID per destination; cost grows with scale.
- **No caller restriction by default** — anyone who has the masking number can
  reach the destination.

**Choose this when:** you only need to protect a small, fixed set of destinations,
you want the simplest possible implementation, and you want callers to be able to
dial in from any phone without registration or PINs.

---

## 14. FAQ

**Q: If it's "one-way", how do both people talk?**
A: The *conversation* is two-way as always. "One-way" only describes how the
mapping is resolved (by destination number only, ignoring the caller).

**Q: Can I reuse one masking number for two destinations?**
A: No. The number *is* the address. One number → one destination, always.

**Q: How is this different from plain call forwarding?**
A: It is call forwarding **with caller-ID masking** — the destination sees the
masking number, not the real caller, and the caller never learns the real
destination number.

**Q: Can I still block some callers?**
A: This strategy allows all by default. If you need blocking, add a check on
`From` (like Strategy 1) — but then it stops being purely one-way.

---

## 15. Glossary

- **One-way mapping:** destination is chosen by the dialled masking number only;
  the caller's identity is ignored.
- **Destination (D1, D2, …):** the real person you are protecting.
- **Forwarding number:** a number that sends every caller to the same place; a
  one-way masking number behaves like one, but also hides the caller.
- **Caller freedom:** the property that any source number can call (no
  registration needed).
- (All Strategy-1 terms — Answer URL, `<Dial>`, `callerId`, bridge, E.164, ngrok —
  still apply; see Strategy 1's glossary.)
