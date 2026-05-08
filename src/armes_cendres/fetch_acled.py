import requests
import duckdb
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
import time

load_dotenv()

ROOT    = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "armes_cendres.duckdb"

def get_token():
    resp = requests.post(
        "https://acleddata.com/oauth/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username":   os.getenv("ACLED_EMAIL"),
            "password":   os.getenv("ACLED_PASSWORD"),
            "grant_type": "password",
            "client_id":  "acled",
            "scope":      "authenticated"
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def fetch_country(token, country, start="1990-01-01", end="2024-12-31"):
    all_rows = []
    page = 1
    while True:
        resp = requests.get(
            "https://acleddata.com/api/acled/read",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "_format":        "json",
                "country":        country,
                "event_date":     f"{start}|{end}",
                "event_date_where": "BETWEEN",
                "fields":         "event_date|year|country|fatalities|event_type",
                "limit":          5000,
                "page":           page,
            }
        )
        data = resp.json()
        rows = data.get("data", [])
        if not rows:
            break
        all_rows.extend(rows)
        print(f"  {country} p{page} → {len(rows)} events")
        if len(rows) < 5000:
            break
        page += 1
        time.sleep(0.5)
    return all_rows

def main():
    # Récupère la liste des pays SIPRI
    con = duckdb.connect(str(DB_PATH))
    countries = [r[0] for r in con.execute(
        "SELECT DISTINCT recipient FROM raw_sipri WHERE recipient IS NOT NULL ORDER BY 1"
    ).fetchall()]
    con.close()

    print(f"{len(countries)} pays à fetcher")

    token = get_token()
    all_data = []

    for i, country in enumerate(countries):
        print(f"[{i+1}/{len(countries)}] {country}")
        try:
            rows = fetch_country(token, country)
            all_data.extend(rows)
        except Exception as e:
            print(f"  ⚠️  {country} : {e}")
        time.sleep(0.3)

    if not all_data:
        print("Aucune donnée récupérée")
        return

    df = pd.DataFrame(all_data)
    print(f"\nTotal events : {len(df)}")

    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS raw_acled")
    con.execute("CREATE TABLE raw_acled AS SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM raw_acled").fetchone()[0]
    con.close()

    print(f"✅ raw_acled chargée : {count} lignes → {DB_PATH}")

if __name__ == "__main__":
    main()
