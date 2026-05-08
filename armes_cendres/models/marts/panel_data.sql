WITH countries AS (
    SELECT DISTINCT country FROM {{ ref('stg_sipri') }}
),

years AS (
    SELECT UNNEST(range(1990, 2025)) AS year
),

grid AS (
    SELECT c.country, y.year
    FROM countries c
    CROSS JOIN years y
),

sipri_agg AS (
    SELECT
        country,
        year_order                          AS year,
        SUM(CAST(NULLIF(tiv_delivered, '') AS DOUBLE)) AS tiv_delivered
    FROM {{ ref('stg_sipri') }}
    WHERE tiv_delivered IS NOT NULL
    GROUP BY country, year_order
),

acled_agg AS (
    SELECT
        country,
        year,
        SUM(total_events)     AS conflict_events,
        SUM(total_fatalities) AS conflict_fatalities
    FROM {{ ref('stg_acled') }}
    GROUP BY country, year
)

SELECT
    g.country,
    g.year,
    COALESCE(s.tiv_delivered, 0)        AS tiv_delivered,
    COALESCE(a.conflict_events, 0)      AS conflict_events,
    COALESCE(a.conflict_fatalities, 0)  AS conflict_fatalities
FROM grid g
LEFT JOIN sipri_agg  s ON s.country = g.country AND s.year = g.year
LEFT JOIN acled_agg  a ON a.country = g.country AND a.year = g.year
ORDER BY g.country, g.year
