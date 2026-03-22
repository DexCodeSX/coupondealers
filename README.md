# Scanned leaked scammers coupondealers.com

[coupondealers.com](https://coupondealers.com/#)
[open source](https://github.com/DexCodeSX/coupondealers/blob/main/ok.py)
[credit by Bisam](https://github.com/DexCodeSX)

## What is this?

coupondealers.com runs a CPA locker scam. They show "free coupons" behind a content locker that forces users to complete shady offers (install apps, enter personal data) before revealing a coupon code.

**The joke:** their API returns every coupon code in plaintext with zero authentication.

```
GET https://coupondealers.com/api/coupons/{id}
```

No cookies. No tokens. No auth. Full coupon code in the JSON response. The entire locker flow is theater.

## How it works

- The site uses Alpine.js with a fake 3-step "verification" modal
- Step 1: fake progress bar ("Checking coupon validity...")
- Step 2: content locker redirects to appsponsor.org (OGAds affiliate 231837)
- Step 3: user must complete 2 CPA offers to "unlock" the code
- Meanwhile the code was already fetched from the API and sitting in browser memory

The "uses today" counter is `Math.floor(Math.random() * 50) + 20` — completely random. The ratings are hardcoded. The "available coupons" counter is random between 120-550.

## Usage

**Zero dependencies. Just Python 3.**

```bash
# scan all coupons (IDs 1-50)
python ok.py

# scan specific range
python ok.py scan 20 40

# fetch single coupon
python ok.py get 36

# dump as JSON
python ok.py json

# dump range as JSON
python ok.py json 20 40
```

## Platform support

| Platform | Command |
|----------|---------|
| Windows | `python ok.py` |
| Linux | `python3 ok.py` |
| macOS | `python3 ok.py` |
| Termux (Android) | `python ok.py` |

On Termux install python first: `pkg install python`

## Tech stack (the scam)

- **Frontend:** PHP 8.2.30, Alpine.js, Bootstrap 5.3.2, jQuery 2.1.4
- **CDN/WAF:** Cloudflare
- **Proxy:** OpenResty 1.27.1.1
- **Locker:** OGAds (appsponsor.org) — affiliate ID 231837
- **Realtime:** Pusher WebSocket (key: `2a1ddc1f29b22896b26c`, cluster: `mt1`)
- **Offers:** jump.offerclk.net CPA network
- **Template:** CounterMind / marketing-rhino.com

## Disclaimer

For educational and research purposes only.
