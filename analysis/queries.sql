-- Queries

-- Média de valor total

SELECT 
    month(tpep_pickup_datetime) AS mes,
    round(avg(total_amount), 2) AS media_valor_total
FROM "db_analytics"."ifood-analyticsyellow_taxi_silver"
WHERE total_amount > 0 -- Garantia extra de qualidade
GROUP BY 1
ORDER BY 1;


-- Média de passageiros por hora no mês de Maio - 2023

SELECT 
    hour(tpep_pickup_datetime) AS hora_dia,
    round(avg(passenger_count), 2) AS media_passageiros
FROM "db_analytics"."ifood-analyticsyellow_taxi_silver"
WHERE month(tpep_pickup_datetime) = 5
  AND passenger_count IS NOT NULL
GROUP BY 1
ORDER BY 1;
