import os
import requests
import boto3
from dotenv import load_dotenv

load_dotenv()

def ingest():
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY")
    )
    bucket = os.getenv("BUCKET_NAME")
    months = ['01', '02', '03', '04', '05']
    
    for m in months:
        url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-{m}.parquet"
        print(f"📥 A descarregar mês {m}...")
        res = requests.get(url)
        if res.status_code == 200:
            s3.put_object(Bucket=bucket, Key=f"landing/taxi_{m}.parquet", Body=res.content)
            print(f"✅ Mês {m} guardado na Landing Zone.")

if __name__ == "__main__":
    ingest()
