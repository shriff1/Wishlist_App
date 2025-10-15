from contextlib import contextmanager
from playwright.sync_api import sync_playwright

@contextmanager
def launch_browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        try:
            yield browser
        finally:
            browser.close()

class PlaywrightPriceAdapter:
    def __init__(self):
        self.browser = None

    def _ensure_browser(self):
        if not self.browser:
            self._ctx = launch_browser()

    def fetch_price(self, url:str, css_selector: str) -> float:
        self._ensure_browser()
        context = self.browser.new_contex(
            user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/123.0.0.0 Safari/537.36"),
            locale ="en-CA",
            viewport = {"width": 1366, "height": 900},
        )
        context.route("**/*", lambda route: route.abort() if route.request.resource_type in {"image","media","font"} else route.continue_())
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            page.wait_for_timeout(800)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
            page.wait_for_timeout(400)

            el = page.wait_for_selector(css_selector, timeout=15000, state="visible")
            text = el.inner_text().strip()

            import re
            m = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)", text)
            if not m:
                raise ValueError(f"Could not parse price from: {text}")
            return float(m.group(1).replace(",", ""))
        finally:
            context.close()

    def __del__(self):
        try:
            if hasattr(self, "_ctx"):
                self._ctx.__exit__(None,None,None)
        except Exception:
            pass

