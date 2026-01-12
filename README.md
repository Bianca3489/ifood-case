# NYC Taxi Data Architecture Case - iFood 🚕

Este repositório contém a solução completa para o case de ingestão, modelagem e análise dos dados de Yellow Taxis de Nova York (Janeiro a Maio de 2023).

## 🏗️ Arquitetura da Solução (Medallion)

A solução foi desenhada seguindo o padrão **Data Lakehouse**, utilizando a arquitetura de medalhão para garantir a qualidade dos dados:

- **Landing Zone (Bronze):** Dados brutos extraídos da API oficial e persistidos em AWS S3 no formato original Parquet.
- **Silver Zone:** Dados harmonizados e modelados em formato **Delta Lake**, permitindo transações ACID e Schema Enforcement.

## 🧠 Desafios Técnicos e Resolução

Como **Data Architect**, foquei na resiliência do pipeline contra o **Schema Drift**:

1. **Inconsistência de Tipos (Mês 01):** Identifiquei que o arquivo de Janeiro/2023 possuía a coluna `passenger_count` como `Double`, enquanto os outros meses utilizavam `Long`.
   - **Solução:** Implementei uma **Harmonização Manual** através de uma função de leitura atômica com casting explícito, unificando os DataFrames via `unionByName` apenas após a padronização.
   
2. **Erro no Leitor Vetorizado do Spark:** Devido a metadados conflitantes no Parquet, o Spark lançava `ClassCastException`.
   - **Solução:** Desabilitei o `spark.sql.parquet.enableVectorizedReader`, permitindo que o Spark realizasse a conversão de tipos de forma flexível durante a ingestão.

3. **Segurança de Credenciais:** As chaves AWS foram protegidas utilizando variáveis de ambiente e arquivos `.env`, seguindo as melhores práticas de segurança (DevSecOps).

## 📁 Estrutura do Projeto

- `src/ingestion.py`: Script de ingestão API -> S3.
- `src/processing.py`: Pipeline de limpeza, harmonização e modelagem Delta.
- `src/analysis.py`: Scripts PySpark para as perguntas de negócio.
- `analysis/queries.sql`: Queries SQL equivalentes para consulta via Metastore.

## 📊 Modelagem e Resultados

As tabelas foram modeladas e criadas do zero no Data Lake:
- **Tabela:** `ifood_db.yellow_taxi`
- **Formato:** Delta Lake
- **Localização:** `s3a://ifood-case-nyc-data-lake/silver/`

### Resultados Finais:
- **Análise 1:** Média de faturamento total (`total_amount`) por mês.
- **Análise 2:** Média de passageiros por hora no mês de Maio.

---
**Desenvolvido por:** Bianca Rodrigues
