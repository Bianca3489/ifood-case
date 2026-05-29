"""
download_to_s3.py
-----------------
Script local para download dos arquivos NYC TLC e upload para S3.
Necessário pois o Databricks Serverless nao tem acesso a internet externa.

Uso:
    python3 -m venv ifood-env
    source ifood-env/bin/activate
    pip install boto3 requests
    python src/ingestion/download_to_s3.py

Credenciais: configure via variavel de ambiente ou AWS CLI
    export AWS_ACCESS_KEY_ID=sua_key
    export AWS_SECRET_ACCESS_KEY=sua_secret
"""

import boto3
import requests
import os
import logging
from botocore.exceptions import ClientError
from requests.adapters import HTTPAdapter
# pyrefly: ignore [missing-import]
from urllib3.util.retry import Retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# Credenciais via variavel de ambiente — nunca hardcoded
AWS_ACCESS_KEY_ID     = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_REGION            = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET             = os.environ.get("S3_BUCKET", "ifood-case-datalake")

TLC_BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
YEAR         = "2023"
MONTHS       = ["01", "02", "03", "04", "05"]

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)

# HTTP session com retry automatico (resiliencia contra erros transientes)
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def _exists(key):
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise

def ingest_month(month):
    filename = f"yellow_tripdata_{YEAR}-{month}.parquet"
    url      = f"{TLC_BASE_URL}/{filename}"
    s3_key   = f"bronze/nyc_taxi/yellow/year={YEAR}/month={month}/{filename}"

    if _exists(s3_key):
        log.info(f"Ja existe: {filename}")
        return {"month": month, "status": "skipped"}

    log.info(f"Baixando: {filename}")
    resp = session.get(url, stream=True, timeout=180)
    resp.raise_for_status()
    content_length = int(resp.headers.get("content-length", 0))
    mb = content_length / 1_048_576
    log.info(f"Subindo ~{mb:.1f} MB -> s3://{S3_BUCKET}/{s3_key}")
    # Streaming direto HTTP -> S3 (sem carregar tudo na RAM)
    resp.raw.decode_content = True
    s3.upload_fileobj(resp.raw, S3_BUCKET, s3_key)
    log.info(f"OK: {filename} (~{mb:.1f} MB)")
    return {"month": month, "status": "uploaded", "mb": round(mb, 1)}

if __name__ == "__main__":
    log.info(f"=== Download NYC TLC {YEAR} -> S3 ===")
    results = []
    for month in MONTHS:
        results.append(ingest_month(month))
    log.info("=== Resumo ===")
    for r in results:
        icon = "OK" if r["status"] in ("uploaded","skipped") else "ERRO"
        info = f"{r.get('mb','')} MB" if r["status"] == "uploaded" else r["status"]
        log.info(f"  [{icon}] Mes {r['month']} -> {info}")
