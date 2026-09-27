-- ============================================================
-- DATA QUALITY & EXCEPTION MONITORING
-- SQL ANALYSIS QUERIES
-- Database: SQLite
-- ============================================================


-- ============================================================
-- 1. Overall Data Quality Summary
-- ============================================================

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


-- ============================================================
-- 2. Exception Count by Rule
-- ============================================================

SELECT
    exception_rule,
    severity,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records
FROM exceptions
GROUP BY
    exception_rule,
    severity
ORDER BY
    exception_count DESC;


-- ============================================================
-- 3. Exception Distribution by Source System
-- ============================================================

SELECT
    source_system,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records
FROM exceptions
GROUP BY source_system
ORDER BY exception_count DESC;


-- ============================================================
-- 4. Data Quality by Source System
-- ============================================================

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
GROUP BY source_system
ORDER BY quality_score ASC;


-- ============================================================
-- 5. Exception Distribution by Region
-- ============================================================

SELECT
    region,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records
FROM exceptions
GROUP BY region
ORDER BY exception_count DESC;


-- ============================================================
-- 6. Monthly Exception Trend
-- ============================================================

SELECT
    strftime('%Y-%m', transaction_date) AS month,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records
FROM exceptions
GROUP BY month
ORDER BY month;


-- ============================================================
-- 7. High Severity Exceptions
-- ============================================================

SELECT
    transaction_id,
    customer_id,
    transaction_date,
    region,
    source_system,
    exception_rule,
    severity,
    affected_field,
    description,
    status
FROM exceptions
WHERE severity = 'High'
ORDER BY transaction_date DESC;


-- ============================================================
-- 8. Transactions with Multiple Data Quality Issues
-- ============================================================

SELECT
    transaction_id,
    COUNT(*) AS issue_count
FROM exceptions
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY issue_count DESC;


-- ============================================================
-- 9. Source System Quality Ranking
-- ============================================================

WITH source_quality AS (

    SELECT
        source_system,

        COUNT(*) AS total_records,

        SUM(
            CASE
                WHEN data_quality_status = 'Valid'
                THEN 1
                ELSE 0
            END
        ) AS valid_records

    FROM transactions
    GROUP BY source_system
)

SELECT
    source_system,
    total_records,
    valid_records,

    ROUND(
        100.0 * valid_records / total_records,
        2
    ) AS quality_score,

    RANK() OVER (
        ORDER BY
            100.0 * valid_records / total_records DESC
    ) AS quality_rank

FROM source_quality
ORDER BY quality_rank;


-- ============================================================
-- 10. Exception Severity Distribution
-- ============================================================

SELECT
    severity,
    COUNT(*) AS exception_count,
    COUNT(DISTINCT transaction_id) AS affected_records,

    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM exceptions),
        2
    ) AS percentage_of_exceptions

FROM exceptions
GROUP BY severity
ORDER BY exception_count DESC;


-- ============================================================
-- 11. Top Problem Areas by Source and Rule
-- ============================================================

SELECT
    source_system,
    exception_rule,
    COUNT(*) AS exception_count
FROM exceptions
GROUP BY
    source_system,
    exception_rule
ORDER BY exception_count DESC
LIMIT 15;


-- ============================================================
-- 12. Exception Rate by Source System
-- ============================================================

WITH source_metrics AS (

    SELECT
        source_system,

        COUNT(*) AS total_records,

        SUM(
            CASE
                WHEN data_quality_status = 'Exception'
                THEN 1
                ELSE 0
            END
        ) AS exception_records

    FROM transactions
    GROUP BY source_system
)

SELECT
    source_system,
    total_records,
    exception_records,

    ROUND(
        100.0 * exception_records / total_records,
        2
    ) AS exception_rate

FROM source_metrics
ORDER BY exception_rate DESC;