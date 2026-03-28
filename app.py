from flask import Flask, jsonify, request, render_template
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "shopping.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                unit TEXT DEFAULT '',
                bought INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/items", methods=["GET"])
def get_items():
    with get_db() as conn:
        items = conn.execute(
            "SELECT * FROM items ORDER BY bought ASC, created_at DESC"
        ).fetchall()
        return jsonify([dict(i) for i in items])


@app.route("/api/items", methods=["POST"])
def add_item():
    data = request.json
    name = data.get("name", "").strip()
    quantity = int(data.get("quantity", 1))
    unit = data.get("unit", "").strip()

    if not name:
        return jsonify({"error": "Name is required"}), 400

    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO items (name, quantity, unit) VALUES (?, ?, ?)",
            (name, quantity, unit)
        )
        conn.commit()
        item = conn.execute(
            "SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify(dict(item)), 201


@app.route("/api/items/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    data = request.json
    fields = []
    values = []

    if "name" in data:
        fields.append("name = ?")
        values.append(data["name"].strip())
    if "quantity" in data:
        fields.append("quantity = ?")
        values.append(int(data["quantity"]))
    if "unit" in data:
        fields.append("unit = ?")
        values.append(data["unit"].strip())
    if "bought" in data:
        fields.append("bought = ?")
        values.append(1 if data["bought"] else 0)

    if not fields:
        return jsonify({"error": "Nothing to update"}), 400

    values.append(item_id)
    with get_db() as conn:
        conn.execute(
            f"UPDATE items SET {', '.join(fields)} WHERE id = ?", values
        )
        conn.commit()
        item = conn.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if not item:
            return jsonify({"error": "Not found"}), 404
        return jsonify(dict(item))


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


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)


init_db()
