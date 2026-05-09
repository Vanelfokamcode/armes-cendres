import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "armes_cendres.duckdb"

app = FastAPI(title="Armes & Cendres API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def query(sql: str):
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df  = con.execute(sql).df()
    con.close()
    return df.to_dict(orient="records")


@app.get("/")
def root():
    return {"status": "ok", "project": "Armes & Cendres"}


@app.get("/countries")
def countries():
    return query("SELECT DISTINCT country FROM panel_data ORDER BY country")


@app.get("/panel/{country}")
def panel(country: str):
    return query(f"""
        SELECT year, tiv_delivered, conflict_events, conflict_fatalities
        FROM panel_data
        WHERE country = '{country}'
        ORDER BY year
    """)


@app.get("/granger")
def granger(significant_only: bool = False):
    where = "WHERE significant = true" if significant_only else ""
    return query(f"""
        SELECT country, lag, pvalue, significant
        FROM granger_results
        {where}
        ORDER BY pvalue
    """)


@app.get("/granger/{country}")
def granger_country(country: str):
    return query(f"""
        SELECT lag, pvalue, significant
        FROM granger_results
        WHERE country = '{country}'
        ORDER BY lag
    """)


@app.get("/top")
def top(n: int = 10):
    return query(f"""
        SELECT country, SUM(tiv_delivered) as tiv_total, SUM(conflict_events) as conflicts_total
        FROM panel_data
        GROUP BY country
        ORDER BY tiv_total DESC
        LIMIT {n}
    """)
