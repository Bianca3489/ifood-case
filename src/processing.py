from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from functools import reduce
import os
from dotenv import load_dotenv

load_dotenv()

def process():
    spark = SparkSession.builder.appName("IFoodProcessing").getOrCreate()
    
    # Bypass de erro de schema (Vectorized Reader)
    spark.conf.set("spark.sql.parquet.enableVectorizedReader", "false")
    spark.conf.set("fs.s3a.access.key", os.getenv("AWS_ACCESS_KEY"))
    spark.conf.set("fs.s3a.secret.key", os.getenv("AWS_SECRET_KEY"))
    
    bucket = os.getenv("BUCKET_NAME")
    
    def read_and_standardize(m):
        path = f"s3a://{bucket}/landing/taxi_{m}.parquet"
        # Harmonização manual para resolver o conflito entre o Mês 01 e os restantes
        return spark.read.parquet(path).select(
            col("VendorID").cast("int"),
            col("passenger_count").cast("int"),
            col("total_amount").cast("double"),
            col("tpep_pickup_datetime").cast("timestamp"),
            col("tpep_dropoff_datetime").cast("timestamp")
        )

    print("🚀 A iniciar harmonização dos meses...")
    dfs = [read_and_standardize(m) for m in ['01', '02', '03', '04', '05']]
    df_final = reduce(lambda x, y: x.unionByName(y), dfs)
    
    # MODELAÇÃO FÍSICA: Escrita em formato Delta (suporta ACID e Schema Enforcement)
    path_silver = f"s3a://{bucket}/silver/yellow_taxi_table"
    df_final.write.format("delta").mode("overwrite").save(path_silver)
    
    # MODELAÇÃO LÓGICA: Criação da base de dados e tabela no Metastore
    spark.sql("CREATE DATABASE IF NOT EXISTS ifood_db")
    spark.sql(f"CREATE TABLE IF NOT EXISTS ifood_db.yellow_taxi USING DELTA LOCATION '{path_silver}'")
    print("✨ Camada Silver e Tabela ifood_db.yellow_taxi criadas com sucesso.")

if __name__ == "__main__":
    process()
