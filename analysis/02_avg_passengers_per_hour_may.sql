-- ============================================================
-- ANALISE 2: Media de passageiros por hora — Maio 2023
-- Pergunta: Qual a media de passenger_count por hora do dia
--           no mes de maio considerando todos os taxis da frota?
-- Tabela  : ifood_catalog.silver.yellow_taxi
-- ============================================================

SELECT
    HOUR(pickup_datetime)                       AS hora_do_dia,
    CASE
        WHEN HOUR(pickup_datetime) BETWEEN 0  AND 5  THEN '00-05 Madrugada'
        WHEN HOUR(pickup_datetime) BETWEEN 6  AND 11 THEN '06-11 Manha'
        WHEN HOUR(pickup_datetime) BETWEEN 12 AND 17 THEN '12-17 Tarde'
        WHEN HOUR(pickup_datetime) BETWEEN 18 AND 23 THEN '18-23 Noite'
    END                                         AS periodo_do_dia,
    COUNT(*)                                    AS total_corridas,
    ROUND(AVG(passenger_count), 2)              AS media_passageiros,
    SUM(passenger_count)                        AS total_passageiros
FROM ifood_catalog.silver.yellow_taxi
WHERE year = '2023' AND month = '5'
GROUP BY hora_do_dia, periodo_do_dia
ORDER BY hora_do_dia;
