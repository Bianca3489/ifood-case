# iFood Case Tecnico — Data Architect

Pipeline de dados end-to-end para ingestao, transformacao e analise dos dados
de corridas de taxi amarelo de Nova York (NYC TLC), periodo Janeiro-Maio 2023.

**Stack:** AWS S3 · Databricks Serverless · PySpark · Delta Lake · Unity Catalog · SQL

---

## Arquitetura — Medallion (Bronze / Silver / Gold)

```
NYC TLC Website
      |
      v
[Script Local]          <- download_to_s3.py (Serverless sem internet externa)
      |
      v
S3 Bronze Layer         <- Delta, dado original completo, sem transformacao
      |
      v  PySpark (02_silver_transformation)
S3 Silver Layer         <- Delta Lake, colunas obrigatorias, snake_case, particionado
      |
      v  SQL (03_gold_analysis)
Gold Views              <- Databricks SQL Editor, consumo pelo time de negocio
```

---

## Estrutura do Repositorio

```
ifood-case/
├── notebooks/
│   ├── 00_config.ipynb                  # Credenciais + paths + validacao S3
│   ├── 01_bronze_ingestion.ipynb        # Registro Bronze no Unity Catalog
│   ├── 02_silver_transformation.ipynb   # PySpark: EDA + limpeza + Delta Lake
│   └── 03_gold_analysis.ipynb          # Views SQL Gold + analises do case
├── analysis/
│   ├── 01_avg_total_amount_per_month.sql
│   └── 02_avg_passengers_per_hour_may.sql
├── src/
│   └── ingestion/
│       └── download_to_s3.py           # Download local -> S3
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Configuracao de Credenciais (Databricks Secrets)

As credenciais AWS sao gerenciadas via **Databricks Secrets** — nunca hardcoded.

### 1. Instalar Databricks CLI

```bash
pip install databricks-cli
databricks configure --token  # informe host e token do workspace
```

### 2. Criar scope e secrets

```bash
databricks secrets create-scope --scope ifood-aws
databricks secrets put --scope ifood-aws --key bucket
# Informe o valor: ifood-case-datalake
```

### 3. Configurar acesso S3

O acesso ao S3 e feito via **IAM Role** configurado no Unity Catalog:
- Storage Credential: `ifood-s3-credential`
- External Location: `ifood-s3-location` -> `s3://ifood-case-datalake/`

Nenhuma Access Key e passada ao Spark — autenticacao via IAM Role automaticamente.

---

## Como Executar

### Pre-requisitos

- Databricks workspace com Unity Catalog habilitado
- Catalog `ifood_catalog` criado
- External Location `ifood-s3-location` configurada (ver guia de configuracao)
- Databricks Secrets configurados (ver acima)
- Python 3.9+ com venv (para download local)

### Passo 1 — Download dos arquivos (local)

```bash
python3 -m venv ifood-env
source ifood-env/bin/activate
pip install -r requirements.txt

export AWS_ACCESS_KEY_ID=sua_key
export AWS_SECRET_ACCESS_KEY=sua_secret
export S3_BUCKET=ifood-case-datalake

python src/ingestion/download_to_s3.py
```

### Passo 2 — Importar notebooks no Databricks

```
Workspace -> Home -> botao direito -> Import
```

Importe os 4 notebooks da pasta `notebooks/` na mesma pasta do Workspace.

### Passo 3 — Executar notebooks em ordem

```
00_config -> 01_bronze -> 02_silver -> 03_gold
```

### Passo 4 — Acessar resultados no SQL Editor

```sql
SELECT * FROM ifood_catalog.gold.vw_avg_total_amount_per_month;
SELECT * FROM ifood_catalog.gold.vw_avg_passengers_per_hour_may;
```

---

## Resultados das Analises

### Analise 1 — Media de total_amount por mes

| Mes | Total Corridas | Media | Mediana |
|---|---|---|---|
| Janeiro | 2.918.148 | $27,46 | $20,16 |
| Fevereiro | 2.764.552 | $27,37 | $20,20 |
| Marco | 3.227.414 | $28,29 | $20,62 |
| Abril | 3.110.374 | $28,78 | $20,93 |
| Maio | 3.319.893 | $29,45 | $21,36 |

**Insight:** Tendencia de crescimento ao longo do ano. A mediana consistentemente
menor que a media indica presenca de corridas de alto valor distorcendo a media.

### Analise 2 — Media de passageiros por hora (Maio)

| Periodo | Hora | Media Passageiros |
|---|---|---|
| Madrugada | 00-05 | 1,41 - 1,46 |
| Manha | 06-11 | 1,26 - 1,36 |
| Tarde | 12-17 | 1,38 - 1,40 |
| Noite | 18-23 | 1,38 - 1,43 |

**Insight:** Pico de volume de corridas entre 17h-19h. Madrugada tem media
levemente maior de passageiros por corrida — sugerindo uso em grupos (lazer).

---

## Decisoes Tecnicas

| Decisao | Justificativa |
|---|---|
| AWS S3 | Storage barato, duravel, desacoplado do compute |
| Databricks Serverless | Sem gestao de cluster, escala automatica |
| Unity Catalog | Governanca, lineage, permissoes por camada |
| Medallion Architecture | Rastreabilidade, idempotencia, separacao de responsabilidades |
| Delta Lake na Silver | ACID, schema enforcement, time travel, ZORDER |
| unionByName na Bronze | Resolve schema evolution entre arquivos mensais |
| snake_case na Silver | Padrao de engenharia de dados |
| SQL na Gold | Acessivel para o time de negocio sem conhecimento de PySpark |
| Databricks Secrets | Zero credenciais hardcoded ou em variaveis de ambiente no codigo |
