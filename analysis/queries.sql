-- Queries

-- Média de valor total

SELECT 
    MONTH(tpep_pickup_datetime) AS mes,
    ROUND(AVG(total_amount), 2) AS media_valor_total
FROM ifood_db.yellow_taxi
GROUP BY 1
ORDER BY 1;


-- Média de passageiros por hora no mês de Maio - 2023

SELECT 
    HOUR(tpep_pickup_datetime) AS hora,
    ROUND(AVG(passenger_count), 2) AS media_passageiros
FROM ifood_db.yellow_taxi
WHERE MONTH(tpep_pickup_datetime) = 5
GROUP BY 1
ORDER BY 1;
