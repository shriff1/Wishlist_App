import sqlite3, time

DB_PATH = "pricewatch.db"

def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as con:
        con.execute(
            """CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            selector TEXT,
            target_price REAL,
            last_price REAL,
            currency TEXT DEFAULT 'USD',
            store TEXT,
            created_at INTEGER
        )"""
        )
        con.execute(
            """CREATE TABLE IF NOT EXISTS price_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            price REAL NOT NULL,
            currency TEXT,
            checked_at INTEGER,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )"""
        )

def add_item(url, selector, target_price,  title=None, currency="CAD", store=None):
    with get_conn() as con:
        con.execute("""INSERT INTO items(url, title, selector, target_price, currency, store, created_at)
                       VALUES(?,?,?,?,?,?,?)""",
                    (url, title, selector, target_price, currency, store, int(time.time())))
        con.commit()

def list_items():
    with get_conn() as con:
        cur = con.execute("SELECT id, title, url, target_price, last_price, currency FROM items ORDER BY id DESC")
        return cur.fetchall()
    
def save_price(item_id, price, currency):
    ts = int(time.time())
    with get_conn() as con:
        con.execute("INSERT INTO price_history(item_id, price, currency, checked_at) VALUES(?,?,?,?)",
                    (item_id, price, currency, ts))
        con.execute("UPDATE items SET last_price=? WHERE id=?", (price, item_id))
        con.commit()

def get_items_for_check():
    with get_conn() as con:
        cur = con.execute("SELECT id, url, selector, target_price, currency FROM items")
        return cur.fetchall()
    
def clear_items():
    with get_conn() as con:
        con.execute("DELETE FROM items")
        con.execute("DELETE FROM price_history")
        con.commit()
