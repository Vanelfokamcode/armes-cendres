WITH source AS (
    SELECT * FROM raw_acled
),

cleaned AS (
    SELECT
        country,
        year,
        month,
        SUM(events)     AS total_events,
        SUM(fatalities) AS total_fatalities
    FROM source
    WHERE country IS NOT NULL
      AND year BETWEEN 1990 AND 2024
    GROUP BY country, year, month
)

SELECT * FROM cleaned
