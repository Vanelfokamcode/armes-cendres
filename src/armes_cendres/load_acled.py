import duckdb
import pandas as pd
from pathlib import Path

ROOT    = Path(__file__).parent.parent.parent
DB_PATH = ROOT / "data" / "armes_cendres.duckdb"
RAW     = ROOT / "data" / "raw"

def load_acled():
    df1 = pd.read_excel(RAW / "acled_political_violence.xlsx", sheet_name="Non_HRP")
    df3 = pd.read_excel(RAW / "acled_political_violence.xlsx", sheet_name="HRP_2")

    df = pd.concat([df1, df3], ignore_index=True)
    df.columns = df.columns.str.strip().str.lower()

    print(f"Colonnes : {list(df.columns)}")
    print(f"Lignes   : {len(df)}")
    print(f"Pays     : {df['country'].nunique()}")
    print(f"Années   : {sorted(df['year'].unique())}")

    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS raw_acled")
    con.execute("CREATE TABLE raw_acled AS SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM raw_acled").fetchone()[0]
    con.close()

    print(f"\n✅ raw_acled chargée : {count} lignes → {DB_PATH}")

if __name__ == "__main__":
    load_acled()
