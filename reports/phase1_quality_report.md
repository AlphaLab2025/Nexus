# Relatório de Qualidade dos Dados

                ## Volume das fontes

                | Fonte | Linhas | Colunas |
                | --- | ---: | ---: |
                | orders | 99,441 | 8 |
| customers | 99,441 | 5 |
| items | 112,650 | 7 |
| payments | 103,886 | 5 |
| reviews | 99,224 | 7 |
| products | 32,951 | 9 |
| sellers | 3,095 | 4 |
| categories | 71 | 2 |
| geolocation | 1,000,163 | 5 |
| holidays | 36 | 4 |
| ibge | 27 | 6 |

                ## Base final

                - Arquivo: `data/processed/orders_analytics.csv`
                - Granularidade: uma linha por pedido (`order_id`)
                - Linhas: 99,441
                - Colunas: 45
                - Pedidos entregues com data valida: 96,476
                - Taxa de atraso em pedidos entregues: 8.11%
                - Pedidos duplicados na base final: 0
                - Entregas com prazo negativo: 0

                ## Maiores percentuais de nulos na base final

                | Coluna | Percentual nulo |
                | --- | ---: |
                | `order_delivered_customer_date` | 2.98% |
| `delivery_days` | 2.98% |
| `late_days` | 2.98% |
| `is_late` | 2.98% |
| `distance_km` | 1.27% |
| `seller_lat` | 1.00% |
| `seller_lng` | 1.00% |
| `avg_product_weight_g` | 0.80% |
| `avg_product_volume_cm3` | 0.80% |
| `seller_state_name` | 0.78% |
| `total_freight_value` | 0.78% |
| `sellers_qty` | 0.78% |

                ## Observações de qualidade

                - Pedidos nao entregues foram mantidos na base, mas `is_late` fica vazio porque nao ha como calcular atraso real sem data de entrega.
                - A geolocalizacao foi agregada por prefixo de CEP para evitar duplicidade tecnica no arquivo original.
                - A distancia entre vendedor e cliente e aproximada, baseada nos centroides dos prefixos de CEP.
            