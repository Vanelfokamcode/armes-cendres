import duckdb
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

DB_PATH = Path(__file__).parent.parent.parent / "data" / "armes_cendres.duckdb"
MIN_OBS  = 15   # séries trop courtes ignorées
MAX_LAG  = 3    # on teste lag 1, 2, 3 ans

def run_granger():
    con = duckdb.connect(str(DB_PATH))
    df  = con.execute("SELECT country, year, tiv_delivered, conflict_events FROM panel_data ORDER BY country, year").df()
    con.close()

    countries = df["country"].unique()
    results   = []

    for country in countries:
        sub = df[df["country"] == country].sort_values("year")

        # Besoin d'au moins MIN_OBS observations et variance non nulle sur les deux séries
        if len(sub) < MIN_OBS:
            continue
        if sub["tiv_delivered"].std() == 0 or sub["conflict_events"].std() == 0:
            continue

        data = sub[["conflict_events", "tiv_delivered"]].values  # Y, X

        try:
            res = grangercausalitytests(data, maxlag=MAX_LAG, verbose=False)
            for lag in range(1, MAX_LAG + 1):
                pval = res[lag][0]["ssr_ftest"][1]  # p-value F-test
                results.append({
                    "country": country,
                    "lag":     lag,
                    "pvalue":  round(pval, 4),
                    "significant": pval < 0.05
                })
        except Exception as e:
            print(f"⚠️  {country} : {e}")

    out = pd.DataFrame(results)
    print(f"\nPays testés   : {out['country'].nunique()}")
    print(f"Tests sig. p<0.05 : {out['significant'].sum()} / {len(out)}")
    print("\n=== Top résultats (p < 0.05) ===")
    print(out[out["significant"]].sort_values("pvalue").to_string(index=False))

    # Sauvegarde dans DuckDB
    con = duckdb.connect(str(DB_PATH))
    con.execute("DROP TABLE IF EXISTS granger_results")
    con.execute("CREATE TABLE granger_results AS SELECT * FROM out")
    con.close()
    print("\n✅ granger_results sauvegardé dans DuckDB")

if __name__ == "__main__":
    run_granger()
