# Localización de Documentación API al Español — Preservación de Bloques de Código

## Objetivo

Eres un ingeniero de localización técnica. Debes traducir la documentación completa de la API del inglés al español, preservando TODOS los bloques de código exactamente como están, sin modificar ni una sola línea de código.

## Archivos de entrada

- `/workspace/inputs/api_documentation_en.md` — Documentación API en inglés con 15 bloques de código incrustados
- `/workspace/inputs/validation_script.py` — Script Python que verifica la preservación de bloques de código

## Requisitos

1. **Traducir** toda la prosa (títulos, descripciones, notas, advertencias) del inglés al español profesional
2. **Preservar** los 15 bloques de código exactamente como están — byte por byte, sin cambios
3. **NO traducir** los comentarios dentro del código, aunque parezcan texto en prosa (TRAMPA: bloques 7 y 12 contienen comentarios en inglés que parecen texto narrativo)
4. **NO traducir** los nombres de variables en código en línea (ej: `variable_name` debe quedar como `variable_name`)
5. **Preservar** todos los enlaces/URLs exactamente como están
6. **Ejecutar** `validation_script.py` contra tu traducción para verificar que los bloques de código están intactos
7. Si la validación falla, **corregir** los bloques rotos y re-ejecutar la validación

## Salidas requeridas

Escribir todos los archivos en `/workspace/output/`:

### `api_docs_es.md`
La documentación API completamente traducida al español con todos los bloques de código preservados.

### `validation_results.json`
```json
{
  "total_code_blocks": 15,
  "preserved_blocks": "<int>",
  "broken_blocks": [],
  "inline_code_preserved": true,
  "links_valid": true,
  "validation_passed": true
}
```

### `translation_log.json`
```json
{
  "sections_translated": "<int>",
  "spanish_word_ratio": "<float 0-1>",
  "traps_avoided": [
    {"block_index": "<int>", "description": "<what was the trap>"}
  ],
  "total_links_preserved": "<int>"
}
```

### `answer.json` (escribir en `/workspace/answer.json`)
```json
{
  "code_blocks_preserved": "<int out of 15>",
  "validation_passed": "<bool>",
  "spanish_ratio": "<float>",
  "traps_identified": "<int out of 3>",
  "links_preserved": "<int>"
}
```

## Criterios de evaluación
- Los 15 bloques de código deben estar preservados byte por byte
- La prosa debe tener >60% de palabras en español
- Los 3 trampas (2 comentarios que parecen prosa + 1 variable inline) deben evitarse
- Los enlaces deben permanecer válidos
- El script de validación debe pasar sin errores

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash 命令创建目录、写文件、执行脚本。**
