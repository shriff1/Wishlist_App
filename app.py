import argparse, time
from apscheduler.schedulers.background import BackgroundScheduler
from db import init_db, add_item, list_items, get_items_for_check, save_price
from stores.adapters import StaticPriceAdapter
from stores.play_browser import PlaywrightPriceAdapter
from notify import notify_console, notify_discord

STATIC = StaticPriceAdapter()
BROWSER = PlaywrightPriceAdapter()

def fetch_price_smart(url, selector):
    if selector.startswith("js:"):
        css = selector[3:].strip()
        return BROWSER.fetch_price(url, css)
    else:
        return STATIC.fetch_price(url, selector)

def check_all_once():
    adapter = StaticPriceAdapter()
    items = get_items_for_check()
    for (iid, url, selector, target, currency) in items:
        try:
            price = adapter.fetch_price(url, selector)
            save_price(iid, price, currency)
            if target is not None and price <= float(target):
                msg = f"✅ Price drop: {url}\nCurrent: {price} {currency} ≤ Target: {target} {currency}"
                notify_console(msg); notify_discord(msg)
            else:
                print(f"[{iid}] {price} {currency} @ {url}")
        except Exception as e:
            print(f"[{iid}] Error: {e}")

def run_scheduler(every_minutes=30):
    sched = BackgroundScheduler()
    sched.add_job(check_all_once, "interval", minutes=every_minutes, next_run_time=None)
    sched.start()
    print(f"Scheduler running every {every_minutes} min. Ctrl+C to stop.")
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        sched.shutdown()

def main():
    init_db()
    p = argparse.ArgumentParser(prog="pricewatch")
    sub = p.add_subparsers(dest="cmd")

    addp = sub.add_parser("add", help="Add a new item")
    addp.add_argument("--url", required=True)
    addp.add_argument("--selector", required=True, help="CSS selector that isolates the price")
    addp.add_argument("--target", type=float, required=True)
    addp.add_argument("--title", default=None)
    addp.add_argument("--currency", default="USD")
    addp.add_argument("--store", default=None)

    sub.add_parser("list", help="List items")
    sub.add_parser("check", help="Run one check now")
    runp = sub.add_parser("run", help="Run scheduler")
    runp.add_argument("--every", type=int, default=30, help="Minutes between checks")

    args = p.parse_args()
    if args.cmd == "add":
        add_item(args.url, args.selector, args.target, args.title, args.currency, args.store)
        print("Item added.")
    elif args.cmd == "list":
        for row in list_items():
            iid, title, url, tgt, last, cur = row
            print(f"[{iid}] {title or '(no title)'} | {url}\n  target={tgt} {cur}  last={last} {cur}")
    elif args.cmd == "check":
        check_all_once()
    elif args.cmd == "run":
        run_scheduler(args.every)
    else:
        p.print_help()

if __name__ == "__main__":
    main()
