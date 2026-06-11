# Conciliación de Facturas Multi-Moneda

## Descripción de la tarea

Eres el analista financiero de una empresa multinacional. Debes conciliar facturas de tres fuentes en distintas monedas (USD, EUR, CNY), detectar discrepancias y generar un informe en español.

## Archivos de entrada

- `/workspace/inputs/invoices_usd_en.csv` — Facturas en dólares americanos (inglés)
- `/workspace/inputs/invoices_cny_zh.csv` — Facturas en yuan chino (chino)
- `/workspace/inputs/bank_statement_eur.csv` — Extracto bancario en euros
- `/workspace/inputs/exchange_rates.json` — Tipos de cambio oficiales

## Requisitos

1. Analizar todas las facturas de las 3 fuentes
2. Convertir todos los importes a EUR usando los tipos de cambio proporcionados
3. Conciliar los pagos del extracto bancario con las facturas
4. Detectar TODAS las discrepancias:
   - Diferencias de importe entre factura y pago
   - Pagos duplicados
   - Facturas sin pago correspondiente
5. Calcular totales por moneda y totales convertidos a EUR
6. Generar informe de conciliación en español

## Salida

Guardar en `/workspace/output/`:
- `reconciliation_report_es.md` — Informe completo en español
- `discrepancies.json` — Lista estructurada de discrepancias encontradas
- `converted_totals.json` — Totales por moneda original y convertidos a EUR

Y `/workspace/answer.json`:
```json
{
  "total_invoices": <int>,
  "total_usd": <float>,
  "total_eur": <float>,
  "total_cny": <float>,
  "total_converted_eur": <float>,
  "discrepancies_found": <int>,
  "discrepancy_types": ["amount_mismatch", "duplicate_payment", "missing_invoice"]
}
```

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
