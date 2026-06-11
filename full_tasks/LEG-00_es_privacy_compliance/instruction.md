# Análisis de cumplimiento LFPDPPP

En `/workspace/inputs/` tienes las políticas de privacidad de una empresa (CCPA en inglés, DSGVO en alemán) y extractos de la LFPDPPP mexicana. Necesito un gap analysis completo para saber si la empresa cumple con la ley mexicana.

Lo que espero:
- Mapeo artículo por artículo entre CCPA/DSGVO y LFPDPPP
- Matriz de cumplimiento con estado (✅/⚠️/❌) y brechas detectadas
- Cálculo de riesgo por categoría — escribe un script Python que compute puntajes ponderados
- Glosario trilingüe (es/en/de) de términos legales clave
- Plan de acciones con prioridad P0/P1/P2 y cronograma Gantt simplificado
- Informe final en español con referencias a artículos específicos

Todo en `/workspace/output/`, consolidado en `/workspace/answer.json`.

**重要：所有产出必须写入磁盘文件，不要只回复文本。用 bash/shell 命令创建目录、写文件、执行脚本。**
