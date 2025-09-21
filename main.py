from fastapi import FastAPI, HTTPException, Query
import sqlite3
from typing import List
import os

DB_FILE = "stuff.db"

app = FastAPI()

# Ensure DB setup
@app.on_event("startup")
def startup_populate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create table and populate in one executescript
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS stuff (
            public_id TEXT PRIMARY KEY,
            secret_codes TEXT
        );
    """)

    # Check if empty and populate
    cursor.execute("SELECT COUNT(*) FROM stuff")
    count = cursor.fetchone()[0]

    if count == 0:
        script = """
        BEGIN TRANSACTION;
        """
        for i in range(1, 51):
            script += f"INSERT INTO stuff (public_id, secret_codes) VALUES ('pub_{i}', 'secret_{i}');\n"
        script += "COMMIT;"
        cursor.executescript(script)

    conn.commit()
    conn.close()


@app.get("/get_stuff")
def get_stuff(num_of_rows: str = "5"):

    sql_query = f"SELECT public_id  FROM stuff LIMIT {num_of_rows};"

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        results = []

        # executescript can run multiple statements, capture results if possible
        for i, statement in enumerate(sql_query.split(";")):
            stmt = statement.strip()
            if stmt.upper().startswith("SELECT"):
                cursor.execute(stmt)
                rows = cursor.fetchall()

                for row in rows:
                    results.append(str(row))
                results.append("")  # spacing
    
        conn.commit()
        conn.close()
        return "\n".join(results)


    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid query: {e}")

