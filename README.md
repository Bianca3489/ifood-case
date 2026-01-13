# NYC Taxi Data Architecture Case - iFood 🚕

Este repositório contém a solução completa para o case de ingestão, modelagem e análise dos dados de Yellow Taxis de Nova York (Janeiro a Maio de 2023).

## 🏗️ Arquitetura da Solução (Medallion)

A solução foi desenhada seguindo o padrão **Data Lakehouse**, utilizando a arquitetura de medalhão para garantir a qualidade dos dados:

- **Landing Zone (Bronze):** Dados brutos extraídos da API oficial e persistidos em AWS S3 no formato original Parquet.
- **Silver Zone:** Dados harmonizados e modelados em formato **Delta Lake**, permitindo transações ACID e Schema Enforcement.

## 🧠 Desafios Técnicos e Resolução

Como **Data Engineer/Architect**, foquei na resiliência do pipeline contra o **Schema Drift**:

- Inconsistência de Tipos (Schema Drift): Identifiquei que o arquivo de Janeiro/2023 possuía a coluna passenger_count como Double, enquanto os outros meses utilizavam Long.

Solução: Implementei uma Harmonização Manual através de uma função de leitura atômica com casting explícito, unificando os DataFrames via unionByName apenas após a padronização.

- Erro no Leitor Vetorizado do Spark: Devido a metadados conflitantes no Parquet de diferentes meses, o Spark lançava ClassCastException.

Solução: Desabilitei o spark.sql.parquet.enableVectorizedReader, permitindo que o Spark realizasse a conversão de tipos de forma flexível durante a ingestão.

- Governança com AWS Glue: Configurei um Crawler para ler o local s3://ifood-case-nyc-data-lake/silver/. O Crawler identificou automaticamente o protocolo Delta, mapeando as partições e esquemas para o AWS Glue Data Catalog. Isso eliminou a necessidade de manter clusters Spark ativos para consultas ad-hoc.

- Segurança de Credenciais: As chaves AWS foram protegidas utilizando variáveis de ambiente e arquivos .env, seguindo práticas de DevSecOps.

## 📁 Estrutura do Projeto

- `src/ingestion.py`: Script de ingestão API -> S3.
- `src/processing.py`: Pipeline de limpeza, harmonização e modelagem Delta.
- `analysis/queries.sql`: Queries SQL equivalentes para consulta via Metastore.

## 📊 Modelagem e Resultados

As tabelas foram modeladas e criadas do zero, respeitando a separação entre armazenamento (S3) e metadados (Glue Catalog):

- Tabela Lógica: db_analytics.ifood-analyticsyellow_taxi_silver

- Formato Físico: Delta Lake (Parquet + Delta Log)

- Localização: s3a://ifood-case-nyc-data-lake/silver/

### Resultados Finais:
- **Análise 1:** Média de faturamento total (`total_amount`) por mês.
- **Análise 2:** Média de passageiros por hora no mês de Maio.

---
**Desenvolvido por:** Bianca Rodrigues
