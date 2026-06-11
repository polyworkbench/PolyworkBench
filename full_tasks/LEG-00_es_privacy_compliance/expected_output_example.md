# Informe de Brecha de Cumplimiento — LFPDPPP México

**Versión**: 1.0 (auto-generado por Agente)
**Destinatario**: María González, DPO LATAM
**Fecha**: 2024-11-20
**Alcance**: Comparación de las políticas de privacidad de Acme Cloud (EE.UU. - CCPA y Alemania - DSGVO) frente a LFPDPPP de México, con vistas al lanzamiento Q1 2025.

---

## 1. Resumen Ejecutivo

La política estadounidense presenta **brechas críticas (❌)** principalmente en tres áreas: (i) inexistencia de los derechos ARCO conforme a LFPDPPP arts. 22-25; (ii) cláusula de transferencia internacional restringida a CCPA y silente respecto de México; (iii) ausencia de aviso de privacidad estructurado (Art. 16). La política alemana es **más cercana al cumplimiento parcial (⚠️)** porque DSGVO comparte derechos análogos (acceso, rectificación, supresión) pero usa terminología y plazos distintos (1 mes vs. 20 días LFPDPPP). En total se identifican **6 acciones P0** que deben completarse antes del lanzamiento.

## 2. Matriz de Cumplimiento (resumen)

Ver `matriz_cumplimiento` en JSON adjunto. Síntesis:

| Categoría | CCPA (EN) | DSGVO (DE) | LFPDPPP (MX) | Estado |
|---|---|---|---|---|
| Base legal del tratamiento | Business purpose §2 | Art. 6 Abs. 1 lit. a-f | Arts. 8/9 | ⚠️ ambas requieren mapeo |
| Derechos del titular | Right-to-know/delete §4 | Auskunft/Löschung §4 | ARCO arts. 22-25 | ⚠️ DE / ❌ US |
| Plazo de respuesta | 45 días | 1 mes | 20 días + 15 efectivo | ⚠️ ambos exceden |
| Transferencia internacional | §7 (silente sobre MX) | SCC + DPF §7 | Arts. 36-37 | ❌ US / ⚠️ DE |
| Edad de menores | 13 años §5 | 16 años §5 (BDSG §8) | sin edad fija; consentimiento parental | ⚠️ |
| Notificación de brechas | Sin plazo numérico §9 | 72 h Art. 33 DSGVO | "inmediata" Art. 20 | ⚠️ ambos compatibles si se opera con 72h |
| Aviso de privacidad estructurado | No exigido por CCPA | Implícito en DSGVO Art. 13/14 | Obligatorio Art. 16 LFPDPPP | ❌ |

## 3. Glosario Trilingüe (10 términos críticos)

| ES | EN | DE | Nota |
|---|---|---|---|
| Titular | Data subject / Consumer | Betroffene Person | "Consumer" en CCPA es más restringido que "data subject" |
| Responsable | Business / Controller | Verantwortlicher | LFPDPPP "responsable" cubre ambos roles |
| Encargado | Service provider / Processor | Auftragsverarbeiter | |
| Datos personales sensibles | Sensitive personal information | Besondere Kategorien (Art. 9) | LFPDPPP exige consentimiento expreso y escrito |
| Derechos ARCO | Right to know/delete/correct/opt-out (parcial) | Auskunft/Berichtigung/Löschung/Widerspruch | "Oposición" ≈ Widerspruch pero con matices |
| Aviso de privacidad | Privacy notice | Datenschutzerklärung | LFPDPPP Art. 16 exige contenido mínimo específico |
| Transferencia | Transfer / Sale | Übermittlung | LFPDPPP distingue "transferencia" de "remisión" (Art. 36) |
| Vulneración | Breach | Datenschutzverletzung | |
| Consentimiento expreso | Express consent / Opt-in | Ausdrückliche Einwilligung | LFPDPPP requiere "por escrito" para sensibles |
| Plazo de conservación | Retention period | Speicherdauer | |

## 4. Análisis Categoría por Categoría

### 4.1 Derechos ARCO (❌ EE.UU. / ⚠️ Alemania)

[Fuente: policy_us_ccpa.md, §4] La política estadounidense reconoce *right-to-know, delete, correct, opt-out, limit use of sensitive PI*. Esto cubre parcialmente Acceso, Rectificación, Cancelación, pero **omite explícitamente "Oposición" (right to object)** que LFPDPPP arts. 24 y 8 reconocen como derecho separado. Adicionalmente, el plazo CCPA de 45 días excede los 20 días LFPDPPP.

[Fuente: policy_de_dsgvo.md, §4] DSGVO ofrece todos los derechos ARCO (Auskunft = Acceso; Berichtigung = Rectificación; Löschung = Cancelación; Widerspruch = Oposición), pero el plazo de 1 mes excede los 20 días de LFPDPPP Art. 32.

**Recomendación**: Adoptar el plazo más corto (20 días) para usuarios mexicanos.

### 4.2 Transferencia Internacional (❌ EE.UU. / ⚠️ Alemania)

[Fuente: policy_us_ccpa.md, §7] La cláusula declara que *"the service does not currently offer services subject to LFPDPPP"*. Esto es exactamente la brecha que hay que cerrar: una vez se opere en México, esta declaración se vuelve falsa y la transferencia EE.UU. → MX queda sin base contractual conforme a LFPDPPP arts. 36-37.

[Fuente: policy_de_dsgvo.md, §7] DSGVO usa SCC + Schrems II + DPF. Los SCC pueden adaptarse para MX si se incorporan cláusulas equivalentes a LFPDPPP, pero el DPF no aplica a México.

**Recomendación**: Firmar Acuerdo de Transferencia con cláusulas equivalentes a LFPDPPP entre Acme US y la entidad mexicana, comunicar al titular antes de la primera recolección.

### 4.3 Edad de Menores (⚠️)

[Fuente: policy_us_ccpa.md, §5] 13 años (COPPA + CCPA).
[Fuente: policy_de_dsgvo.md, §5; BDSG §8] 16 años.
[Fuente: lfpdppp_extracts.md, Reglamento Art. 39] Sin edad fija; consentimiento parental obligatorio.

**Recomendación**: Adoptar la regla más estricta (16 años) para LATAM y exigir consentimiento parental explícito. Para sectores regulados (financiero), evaluar 18 años conforme a lineamientos sectoriales mexicanos.

### 4.4 Notificación de Vulneraciones (⚠️)

LFPDPPP exige notificación "inmediata" (Art. 20), sin un plazo numérico. La política alemana usa 72h (DSGVO Art. 33), lo que es **más estricto** que el lenguaje LFPDPPP y por tanto compatible. La política estadounidense (§9) usa "most expedient time possible", aceptable pero menos preciso.

**Recomendación**: Estandarizar a 72h como SLA interno, dado que cumple ambas regulaciones.

### 4.5 Aviso de Privacidad Estructurado (❌)

LFPDPPP Art. 16 exige un *aviso de privacidad* con contenido mínimo (identidad, finalidades, ARCO, transferencias, mecanismos de cambio). Ni la política estadounidense ni la alemana cumplen exactamente esta estructura; deben elaborar un aviso de privacidad **integral, simplificado y corto** específico para titulares mexicanos.

## 5. Acciones Recomendadas (priorizadas)

| # | Acción | Prioridad | Responsable | Plazo |
|---|---|---|---|---|
| AR-1 | Redactar aviso de privacidad LFPDPPP (integral, simplificado, corto) en español neutro de México | P0 | DPO LATAM + legal externo | 2025-01-15 |
| AR-2 | Modificar §7 de la política EE.UU. eliminando la exclusión de LFPDPPP y agregando cláusula de transferencia EE.UU.-MX | P0 | Legal HQ | 2024-12-31 |
| AR-3 | Firmar Acuerdo de Transferencia con cláusulas equivalentes a LFPDPPP entre Acme Inc. y la futura entidad mexicana | P0 | Legal HQ + DPO LATAM | 2025-01-31 |
| AR-4 | Establecer SLA de respuesta a derechos ARCO en 20 días para titulares mexicanos (vs. 45 días CCPA) | P0 | Customer Ops | 2025-02-15 |
| AR-5 | Implementar registro y notificación de vulneraciones a 72h, comunicable al INAI cuando aplique | P1 | Security + Legal | 2025-02-28 |
| AR-6 | Actualizar flujo de registro para validar edad ≥16 años y solicitar consentimiento parental cuando proceda | P1 | Engineering | 2025-02-28 |
| AR-7 | Capacitación interna en LFPDPPP para soporte y ventas LATAM (incluyendo derechos ARCO) | P2 | RR.HH. + DPO | 2025-03-31 |
| AR-8 | Revisión de subprocesadores (Stripe, SendGrid, Datadog) para asegurar cláusulas LFPDPPP-compatibles | P1 | Vendor Mgmt | 2025-03-15 |

---

*Este informe se basa en la información proporcionada y no constituye asesoría legal vinculante. Se recomienda revisión por abogado externo certificado en LFPDPPP antes de la presentación al INAI.*
