# Copilot Instructions for pygments-bsl

## Project Overview
**pygments-bsl** is a Pygments syntax highlighter for 1C languages (BSL and SDBL). It provides lexer classes that tokenize source code into semantic tokens for syntax coloring.

## Architecture & Data Flow

### Three-Layer Architecture
1. **Source Data**: `3rd_party/*.json` files contain 1C keywords, types, methods, and enums (bilingual: Russian + English)
2. **Generated Code**: `tools/generate_data.py` transforms JSON into `pygments_bsl/generated_data.py` (auto-generated tuples of token names)
3. **Lexer**: `pygments_bsl/lexer.py` contains `BslLexer` and `SdblLexer` classes that use generated data to tokenize code

**Critical**: Never edit `generated_data.py` directly. Always update the source JSON files and regenerate via `python tools/generate_data.py`.

### Key Lexer Classes
- **BslLexer** (Business Script Language): Main 1C procedural language lexer
- **SdblLexer** (1C Query Language): SQL-like query language lexer

Both inherit from Pygments' `RegexLexer` and use callback functions for context-sensitive tokenization.

## Key Patterns & Conventions

### Token Categorization via Callbacks
The lexer uses callback functions like `_bsl_name_callback()` that analyze context to emit appropriate token types:
- **Token.Name.Builtin**: Built-in functions (when followed by `(`)
- **Token.Name.Class**: Type/class references
- **Token.Keyword**: Keywords
- **Token.Name.Function** vs **Token.Name.Variable**: Determined by presence of `(` call operator

See `_is_call()` and `_call_has_args()` helper functions—they predict if a name is a function call by looking ahead for `(`.

### Case-Insensitive Matching with Caching
- Use `_casefold(text)` for case normalization (supports Russian)
- Use `_casefold_set()` to create lookups: `lexer._bsl_keyword = _casefold_set(KEYWORD_NAMES)`
- Cached with `@lru_cache(maxsize=4096)` for performance

### Bilingual Support Pattern
Generated data contains both Russian and English variants of keywords:
```python
# From 3rd_party files:
{"name": "Возврат", "name_en": "Return"}
```
Both variants go into the same token set for case-insensitive matching.

### Complex Pattern Examples
- **Locale Strings**: Multi-line strings with interpolation (see `_locale_*` callbacks)
- **Document Type Lists**: Types declared as `из Документ1, Документ2` (Russian "из" = "from")
- **Metadata Navigation**: `РегистрСведений.PropertyName()` requires tokenizing each segment

## Development Workflow

### Common Commands
```bash
# Generate lexer data from JSON (run after 3rd_party/ changes)
python tools/generate_data.py

# Run tests
pytest

# Build package
python -m build

# Local docs (uses local lexer immediately via mkdocs_hooks.py)
pip install mkdocs mkdocs-material
mkdocs serve
```

### CI/CD Workflow
- **test.yml**: Runs `pytest` on push/PR to master
- **publish.yml**: Builds and pushes to PyPI on release creation
- **gh-pages.yml**: (implied) Publishes MkDocs site

## Testing Strategy

### Test Structure (`tests/test_lexer.py`)
- Uses `LexerTestCase` base with `lex_filtered()` (strips whitespace tokens for cleaner assertions)
- `assertTokens()` validates exact token sequences
- Test files in `tests/examplefiles/` (bsl/, sdbl/) provide real-world examples

### Testing Approach
Test changes by:
1. Write test in `test_lexer.py` with expected token output
2. Run `pytest tests/test_lexer.py::YourTestClass::test_name` for quick feedback
3. Use `tests/examplefiles/` for exploratory tokenization testing

## When Modifying the Lexer

### Adding Keywords
1. Update `3rd_party/` JSON files (add bilingual entries)
2. Run `python tools/generate_data.py` to regenerate `generated_data.py`
3. Update lexer rules in `lexer.py` if needed (e.g., add new keyword set)
4. Add test cases in `test_lexer.py`

### Fixing Token Misclassification
1. Identify the problematic pattern in example files or create minimal test case
2. Trace through callback logic (especially context checks in `_bsl_name_callback`, `_sdbl_name_callback`)
3. Modify regex patterns or callback functions
4. Add regression test

### Performance Considerations
- Callbacks are called for every identifier—keep logic minimal
- Use `@lru_cache` for functions called frequently (e.g., `_casefold`)
- Profile with large files if modifying critical paths

## File Organization

- **`pygments_bsl/`**: Package source
  - `lexer.py` (1357 lines): Main lexer implementations & callbacks
  - `__init__.py`: Exports BslLexer, SdblLexer
  - `generated_data.py` (auto-generated): Token name tuples
- **`tools/`**: Scripts for code generation
  - `generate_data.py`: Converts `3rd_party/*.json` to `generated_data.py`
- **`tests/`**: Test suite
  - `test_lexer.py`: Unit tests for tokenization
  - `examplefiles/`: Real code samples (bsl/, sdbl/)
- **`3rd_party/`**: Source data (JSON)
  - `types.json`, `global-methods.json`, `global-properties.json`, `enums.json`
- **`docs/`**: MkDocs documentation
  - Uses local lexer via `mkdocs_hooks.py` during `mkdocs serve`

## 1C Language Specifics

### BSL Keywords (Bilingual)
- Control flow: `Если` / `If`, `Иначе` / `Else`, `Пока` / `While`
- Declarations: `Функция` / `Function`, `Процедура` / `Procedure`
- Exceptions: `Попытка` / `Try`, `Исключение` / `Except`

### SDBL (Query Language)
- SQL-like syntax with 1C-specific extensions
- Metadata references: `Таблица.Реквизит` / `Table.Attribute`
- Aggregate functions: `СУММА` / `SUM`, `КОЛИЧЕСТВО` / `COUNT`

### Token Patterns to Know
- Comments: `//` single-line, `/*...*/` multi-line
- Strings: Single quotes with interpolation: `'Text "with %1 interpolation"'`
- Region markers: `#Область`, `#КонецОбласти` (preprocessor tokens)
- Doc comments: `///@param` style with type annotations in comments

---

**Last Updated**: 2025-01-20  
**Maintainer**: See package metadata in setup.py
