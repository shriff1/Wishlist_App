import re, requests
from bs4 import BeautifulSoup

class StaticPriceAdapter:
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (windows NT 10.0; Win64; x64)"
    }
    def fetch_price(self, url: str, css_selector: str):
        r = requests.get(url, headers=self.HEADERS, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        node = soup.select_one(css_selector)
        if not node:
            raise ValueError("Price element not found; adjust selector.")
        text = node.get_text(strip=True)
        price = self._extract_number(text)
        if price is None:
            raise ValueError(f"Could not parse price from: {text}")
        return price
    @staticmethod
    def _extract_number(s: str):
        m = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)", s)
        if not m: return None
        return float(m.group(1).replace(",", ""))