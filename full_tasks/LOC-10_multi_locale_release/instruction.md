# Task: Multi-Locale Simultaneous Release QA & Coordination

## Background
You are coordinating a simultaneous 6-locale release for a mobile application. Your job is to verify translation consistency across all locales, detect issues, generate a QA report, and produce locale-specific changelogs.

## Input Files
All input files are located in `/workspace/inputs/`:

- `source_en.json` — English source strings with context (50 key-value pairs)
- `translations_zh.json` — Chinese (Simplified) translations
- `translations_ja.json` — Japanese translations
- `translations_ko.json` — Korean translations
- `translations_ru.json` — Russian translations
- `translations_vi.json` — Vietnamese translations
- `translations_fr.json` — French translations
- `release_notes_en.md` — English release notes to localize into changelogs

## Requirements

### QA Report (`qa_report.md`)
- Comprehensive quality assurance report in English
- Cover: completeness check, placeholder consistency, string length issues, terminology consistency
- Document all issues found with severity levels (critical/major/minor)
- Include recommendations for each locale
- Professional release management format

### Consistency Matrix (`consistency_matrix.json`)
- Cross-locale comparison matrix
- For each source string: check presence and placeholder integrity across all 6 locales
- Structure: `{string_key: {locale: {present: bool, placeholders_valid: bool, length_ok: bool, notes: str}}}`
- Summary statistics at the end

### Locale-Specific Changelogs (`changelogs/changelog_*.md`)
- One changelog per locale (zh, ja, ko, ru, vi, fr)
- Translated from `release_notes_en.md`
- Adapted to locale conventions (date format, versioning style)
- Maintain technical accuracy while being natural in each language

### Issues Found (`issues_found.json`)
- Structured list of all detected issues
- Each issue: `{id, locale, string_key, issue_type, severity, description, suggestion}`
- Issue types: missing_string, placeholder_error, inconsistency, length_violation, terminology_error
- Must detect the deliberately embedded issues in the translation files

## Expected Issues to Detect
The translation files contain several deliberate issues that a thorough QA process should identify. Your QA report should find and document these.

## Output Path
All output files should be written to `/workspace/`. Create the `changelogs/` subdirectory as needed.

---

**Important: All outputs must be written to disk files. Do not just reply with text. Use bash commands to create directories, write files, and execute scripts.**
