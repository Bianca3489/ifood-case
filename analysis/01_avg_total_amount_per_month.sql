-- ============================================================
-- ANALISE 1: Media de total_amount por mes (Jan-Mai 2023)
-- Pergunta: Qual a media de valor total (total_amount) recebido
--           em um mes considerando todos os yellow taxis da frota?
-- Tabela  : ifood_catalog.silver.yellow_taxi
-- ============================================================

SELECT
    year                                        AS ano,
    CAST(month AS INT)                          AS mes_numero,
    CASE CAST(month AS INT)
        WHEN 1 THEN 'Janeiro'   WHEN 2 THEN 'Fevereiro'
        WHEN 3 THEN 'Marco'     WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Maio'
    END                                         AS mes_nome,
    COUNT(*)                                    AS total_corridas,
    ROUND(AVG(total_amount), 2)                 AS media_total_amount,
    ROUND(MIN(total_amount), 2)                 AS min_total_amount,
    ROUND(MAX(total_amount), 2)                 AS max_total_amount,
    ROUND(PERCENTILE(total_amount, 0.5), 2)     AS mediana_total_amount,
    ROUND(STDDEV(total_amount), 2)              AS desvio_padrao
FROM ifood_catalog.silver.yellow_taxi
WHERE year = '2023'
GROUP BY year, month
ORDER BY mes_numero;
