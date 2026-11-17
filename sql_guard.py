import re


class SqlRejected(Exception):
    pass


BLOCKED = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|merge|grant|revoke|copy|put|"
    r"call|execute|use|set|remove|undrop|information_schema|account_usage)\b|snowflake\.",
    re.I,
)
MAX_ROWS = 100


def validate_sql(sql: str) -> str:
    """Return a safe version of the query, or raise SqlRejected."""
    s = sql.strip().rstrip(";").strip()
    if not s:
        raise SqlRejected("empty query")
    if ";" in s:
        raise SqlRejected("multiple statements are not allowed")
    if "--" in s or "/*" in s:
        raise SqlRejected("comments are not allowed")
    if not re.match(r"^(select|with)\b", s, re.I):
        raise SqlRejected("only SELECT queries are allowed")
    hit = BLOCKED.search(s)
    if hit:
        raise SqlRejected(f"forbidden keyword: {hit.group(0)}")
    if not re.search(r"\blimit\s+\d+", s, re.I):
        s += f" LIMIT {MAX_ROWS}"
    return s