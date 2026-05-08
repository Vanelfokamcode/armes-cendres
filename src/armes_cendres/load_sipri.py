import duckdb
import pandas as pd
from pathlib import Path

ROOT    = Path(__file__).parent.parent.parent
RAW     = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "armes_cendres.duckdb"

def load_sipri():
    df = pd.read_csv(
        RAW / "trade-register.csv",
        skiprows=11,
        dtype=str,
        encoding="latin-1"
    )

    # Nettoyage noms de colonnes
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )

    print(f"Colonnes : {list(df.columns)}")
    print(f"Lignes   : {len(df)}")
    print(df.head(3))

    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS raw_sipri")
    con.execute("""
        CREATE TABLE raw_sipri AS
        SELECT * FROM df
    """)
    count = con.execute("SELECT COUNT(*) FROM raw_sipri").fetchone()[0]
    con.close()

    print(f"\n✅ raw_sipri chargée : {count} lignes → {DB_PATH}")

if __name__ == "__main__":
    load_sipri()
