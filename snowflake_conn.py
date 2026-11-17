import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
import os
import snowflake.connector
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    with open(os.environ["SNOWFLAKE_KEY_PATH"], "rb") as f:
        key = serialization.load_pem_private_key(f.read(), password=None)
    der = key.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=der,
        role="CLAIMS_READONLY",
        warehouse="CLAIMS_WH",
        database="CLAIMS_DB",
        schema="GOLD",
    )