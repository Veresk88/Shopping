from flask import Flask, jsonify, request, render_template
import sqlite3
import json
import os

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "shopping.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def parse_tags(raw):
    if not raw:
        return ["Family"]
    if raw.startswith("["):
        try:
            tags = json.loads(raw)
            return tags if isinstance(tags, list) and tags else ["Family"]
        except Exception:
            pass
    mapping = {
        "Общее": "Family", "obsh": "Family",
        "ЕА": "YA", "ea": "YA", "Y+A": "YA",
        "ВА": "VA", "va": "VA", "V+A": "VA",
    }
    val = mapping.get(raw, raw)
    return [val]


def item_to_dict(row):
    d = dict(row)
    d["tags"] = parse_tags(d.get("tag", ""))
    return d


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit TEXT DEFAULT '',
                tag TEXT DEFAULT '["Family"]',
                bought INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        try:
            conn.execute('ALTER TABLE items ADD COLUMN tag TEXT DEFAULT \'["Family"]\'')
        except Exception:
            pass
        conn.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/items", methods=["GET"])
def get_items():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY bought ASC, created_at DESC"
        ).fetchall()
        return jsonify([item_to_dict(r) for r in rows])


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.json
    name = data.get("name", "").strip()
    quantity = int(data.get("quantity", 1))
    unit = data.get("unit", "").strip()
    tags = data.get("tags", ["Family"])
    if not isinstance(tags, list) or not tags:
        tags = ["Family"]

    if not name:
        return jsonify({"error": "Name is required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, quantity, unit, tag) VALUES (?, ?, ?, ?)",
            (name, quantity, unit, json.dumps(tags))
        )
        conn.commit()
        row = conn.execute("SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return jsonify(item_to_dict(row)), 201


@app.route("/api/items/bulk", methods=["POST"])
def bulk_add():
    """Add multiple items at once (for preset loading)."""
    items_data = request.json
    if not isinstance(items_data, list):
        return jsonify({"error": "Expected a list"}), 400
    with get_db() as conn:
        for item in items_data:
            name = item.get("name", "").strip()
            if not name:
                continue
            quantity = int(item.get("quantity", 1))
            unit = item.get("unit", "").strip()
            tags = item.get("tags", ["Family"])
            if not isinstance(tags, list) or not tags:
                tags = ["Family"]
            conn.execute(
                "INSERT INTO items (name, quantity, unit, tag) VALUES (?, ?, ?, ?)",
                (name, quantity, unit, json.dumps(tags))
            )
        conn.commit()
    rows = conn.execute("SELECT * FROM items ORDER BY bought ASC, created_at DESC").fetchall()
    return jsonify([item_to_dict(r) for r in rows]), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.json
    fields, values = [], []

    if "name" in data:
        fields.append("name = ?")
        values.append(data["name"].strip())
    if "quantity" in data:
        fields.append("quantity = ?")
        values.append(int(data["quantity"]))
    if "unit" in data:
        fields.append("unit = ?")
        values.append(data["unit"].strip())
    if "tags" in data:
        tags = data["tags"]
        if not isinstance(tags, list) or not tags:
            tags = ["Family"]
        fields.append("tag = ?")
        values.append(json.dumps(tags))
    if "bought" in data:
        fields.append("bought = ?")
        values.append(1 if data["bought"] else 0)

    if not fields:
        return jsonify({"error": "Nothing to update"}), 400

    values.append(item_id)
    with get_db() as conn:
        conn.execute(f"UPDATE items SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
        if not row:
            return jsonify({"error": "Not found"}), 404
        return jsonify(item_to_dict(row))


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    with get_db() as conn:
        conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return jsonify({"ok": True})


@app.route("/api/items/clear-bought", methods=["DELETE"])
def clear_bought():
    with get_db() as conn:
        conn.execute("DELETE FROM items WHERE bought = 1")
        conn.commit()
        return jsonify({"ok": True})


@app.route("/api/items/uncheck-all", methods=["POST"])
def uncheck_all():
    with get_db() as conn:
        conn.execute("UPDATE items SET bought = 0")
        conn.commit()
        return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


init_db()
