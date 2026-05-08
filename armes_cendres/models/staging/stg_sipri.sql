WITH source AS (
    SELECT * FROM raw_sipri
),

cleaned AS (
    SELECT
        recipient                                           AS country,
        CAST(year_of_order AS INTEGER)                     AS year_order,
        weapon_designation,
        weapon_description,
        COALESCE(NULLIF(number_delivered, '?'), NULL)      AS number_delivered_raw,
        COALESCE(NULLIF(sipri_tiv_of_delivered_weapons, ''), NULL) AS tiv_delivered,
        years_of_delivery,
        status,
        comments
    FROM source
    WHERE recipient IS NOT NULL
      AND recipient NOT IN ('unknown recipient(s)', 'NATO**')
      AND year_of_order IS NOT NULL
)

SELECT * FROM cleaned
