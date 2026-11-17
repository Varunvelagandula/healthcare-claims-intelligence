from snowflake_conn import get_conn

conn = get_conn()
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM FACT_CLAIMS")
print("FACT_CLAIMS rows:", cur.fetchone()[0])

try:
    cur.execute("DELETE FROM FACT_CLAIMS")
    print("PROBLEM: delete worked, the role is NOT read-only!")
except Exception as e:
    print("DELETE blocked, as it should be:", str(e)[:120])

conn.close()