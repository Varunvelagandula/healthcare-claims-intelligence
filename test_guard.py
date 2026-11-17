import sys

from sql_guard import validate_sql, SqlRejected

cases = [
    ("SELECT COUNT(*) FROM FACT_CLAIMS", True),
    ("SELECT diagnosis_code, SUM(total_claim_cost) FROM FACT_CLAIMS GROUP BY 1", True),
    ("DELETE FROM FACT_CLAIMS", False),
    ("DROP TABLE FACT_CLAIMS", False),
    ("SELECT 1; DROP TABLE FACT_CLAIMS", False),
    ("UPDATE FACT_CLAIMS SET total_claim_cost = 0", False),
    ("SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY", False),
    ("SELECT 1 -- sneaky", False),
    ("Sorry, I cannot help with that", False),
]
bugs = 0
for sql, should_pass in cases:
    try:
        validate_sql(sql)
        ok = True
    except SqlRejected:
        ok = False
    if ok != should_pass:
        bugs += 1
    print("OK  " if ok == should_pass else "BUG ", sql[:60])

sys.exit(1 if bugs else 0)