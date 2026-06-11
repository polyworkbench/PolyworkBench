# Reconstrucción de Cadena de Evidencia: Caso Transferencias Internacionales

## Objetivo

Usted es un analista forense legal encargado de reconstruir la cadena de eventos en un caso de transferencias financieras internacionales sospechosas. Se le proporcionan los siguientes documentos en tres idiomas:

1. `declaraciones_testigos.md` — Declaraciones de tres testigos (Español)
2. `forensic_accounting_report.md` — Informe de contabilidad forense (Inglés)
3. `bank_transfer_records_zh.md` — Registros bancarios de transferencias (Chino)

## Tarea

Analice todos los documentos para:

1. **Reconstruir la cronología completa** de eventos, resolviendo cualquier inconsistencia entre las fuentes.
2. **Calcular los montos financieros totales** con conversiones de divisas correctas.
3. **Identificar inconsistencias testimoniales** entre los testigos.
4. **Establecer la cadena de evidencia** que conecta las transferencias con los eventos documentados.

## Archivos de Salida Requeridos

### `cadena_evidencia.md`
Informe en español que contenga:
- Resumen ejecutivo del caso
- Cronología verificada de eventos con fuentes
- Análisis de inconsistencias testimoniales
- Conclusiones sobre la cadena de evidencia
- Recomendaciones para la investigación

### `timeline.json`
```json
{
  "events": [
    {
      "date": "YYYY-MM-DD",
      "event": "<descripción>",
      "sources": ["<fuente1>", "<fuente2>"],
      "confidence": "<confirmed|disputed|single_source>",
      "notes": "<observaciones>"
    }
  ],
  "witness_inconsistencies": [
    {
      "topic": "<tema>",
      "witness_a": "<lo que dice A>",
      "witness_b": "<lo que dice B>",
      "witness_c": "<lo que dice C>",
      "resolution": "<resolución propuesta>"
    }
  ]
}
```

### `financial_summary.json`
```json
{
  "transfers": [
    {
      "id": "<transfer_id>",
      "date": "YYYY-MM-DD",
      "amount_cny": <float>,
      "amount_usd": <float>,
      "exchange_rate": <float>,
      "source_account": "<cuenta origen>",
      "destination_account": "<cuenta destino>"
    }
  ],
  "total_cny": <float>,
  "total_usd": <float>,
  "exchange_rate_used": <float>
}
```

## Criterios de Evaluación
- Cronología correcta: fechas y secuencia verificada
- Totales financieros: ¥7.2M total, ~$1.08M USD
- Inconsistencia testimonial: Testigo A dice 16 de enero (incorrecto), real es 15 de enero
- Completitud: todos los eventos y transferencias documentados

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
