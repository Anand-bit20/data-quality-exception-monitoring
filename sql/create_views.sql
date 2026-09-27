-- ============================================================
-- POWER BI DATA QUALITY VIEWS
-- ============================================================


-- 1. Overall Quality Metrics

CREATE VIEW IF NOT EXISTS vw_quality_summary AS

SELECT
    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN data_quality_status = 'Valid'
            THEN 1
            ELSE 0
        END
    ) AS valid_records,

    SUM(
        CASE
            WHEN data_quality_status = 'Exception'
            THEN 1
            ELSE 0
        END
    ) AS exception_records,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN data_quality_status = 'Valid'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS quality_score

FROM transactions;


-- 2. Quality by Source

CREATE VIEW IF NOT EXISTS vw_source_quality AS

SELECT
    source_system,

    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN data_quality_status = 'Valid'
            THEN 1
            ELSE 0
        END
    ) AS valid_records,

    SUM(
        CASE
            WHEN data_quality_status = 'Exception'
            THEN 1
            ELSE 0
        END
    ) AS exception_records,

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN data_quality_status = 'Valid'
                THEN 1
                ELSE 0
            END
        ) / COUNT(*),
        2
    ) AS quality_score

FROM transactions

GROUP BY source_system;


-- 3. Exception Analysis

CREATE VIEW IF NOT EXISTS vw_exception_analysis AS

SELECT
    exception_rule,
    severity,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records

FROM exceptions

GROUP BY
    exception_rule,
    severity;


-- 4. Exception by Source

CREATE VIEW IF NOT EXISTS vw_exception_by_source AS

SELECT
    source_system,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records

FROM exceptions

GROUP BY source_system;


-- 5. Exception by Region

CREATE VIEW IF NOT EXISTS vw_exception_by_region AS

SELECT
    COALESCE(region, 'Unknown') AS region,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records

FROM exceptions

GROUP BY
    COALESCE(region, 'Unknown');


-- 6. Monthly Exception Trend

CREATE VIEW IF NOT EXISTS vw_monthly_exceptions AS

SELECT
    strftime('%Y-%m', transaction_date) AS month,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records

FROM exceptions

GROUP BY
    strftime('%Y-%m', transaction_date)

ORDER BY month;


-- 7. Exception Detail

CREATE VIEW IF NOT EXISTS vw_exception_details AS

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    COALESCE(region, 'Unknown') AS region,
    source_system,
    exception_rule,
    severity,
    affected_field,
    description,
    status

FROM exceptions;

CREATE VIEW IF NOT EXISTS vw_exception_severity AS
SELECT
    severity,
    COUNT(*) AS exception_count
FROM exceptions
GROUP BY severity;