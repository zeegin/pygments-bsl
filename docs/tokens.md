# Pygments tokens usage

This document explains how BSL/SDBL lexers map code to Pygments tokens and how those tokens become CSS classes in Material for MkDocs. It is meant to help you build custom themes with predictable syntax colors.

## How to read this file

Each token becomes a CSS class in the rendered HTML. Material for MkDocs then maps those classes to CSS variables like `--md-code-hl-keyword-color`. If a token has an empty flag, it means the lexer does not emit it.

## Theming quick start

If you only want a solid base theme, focus on these CSS variables first:

- `--md-code-hl-keyword-color` (keywords, control flow)
- `--md-code-hl-function-color` (functions, types, namespaces)
- `--md-code-hl-variable-color` (variables, properties)
- `--md-code-hl-string-color` (strings, string escapes)
- `--md-code-hl-number-color` (numbers)
- `--md-code-hl-comment-color` (comments, doc sections)
- `--md-code-hl-operator-color` (operators)
- `--md-code-hl-punctuation-color` (punctuation)

Then refine:

- `--md-code-hl-special-color` (escapes, preprocessor, special strings)
- `--md-code-hl-constant-color` (builtins, constants)
- `--md-code-hl-generic-color` (errors, generic output)

For full customization details, see the Material for MkDocs guide:
[Material for MkDocs: Custom syntax theme](https://squidfunk.github.io/mkdocs-material/reference/code-blocks/#custom-syntax-theme)

## BSL-focused examples

These snippets show how the lexer typically classifies elements. Use them as a visual target when adjusting your palette.

```bsl
// Параметры:
//   Период - Дата - период расчета
```

Expected tokens:

- `//` and doc text: `Comment.Single`
- `Параметры`: `Keyword`
- `Период`: `Name.Variable`
- `Дата`: `Name.Class`
- `-` and `:`: `Punctuation`

```bsl
Если ЗначениеЗаполнено(Период) Тогда
    Сообщить("ОК");
КонецЕсли;
```

Expected tokens:

- `Если`, `Тогда`, `КонецЕсли`: `Keyword`
- `ЗначениеЗаполнено`: `Name.Builtin`
- `Период`: `Name.Variable`
- `"ОК"`: `Literal.String`
- `(`, `)`, `;`: `Punctuation`

```bsl
// РеквизитыКомпонент - Массив из см. ВнешниеКомпоненты.РеквизитыКомпоненты
```

Expected tokens:

- `РеквизитыКомпонент`: `Name.Variable`
- `Массив`: `Name.Class`
- `из`, `см.`: `Keyword`
- `ВнешниеКомпоненты.РеквизитыКомпоненты`: `Name.Class`

## SDBL-focused examples

```sdbl
ВЫБРАТЬ
    ПОЛЕ
ИЗ Таблица
```

Expected tokens:

- `ВЫБРАТЬ`, `ИЗ`: `Keyword.Declaration`
- `ПОЛЕ`: `Name.Variable`
- `Таблица`: `Name.Class`

## Full token list

Below is the list of standard Pygments tokens and whether they are used by the BSL or SDBL lexers in this project. Columns show usage flags, the Material for MkDocs CSS class, and the palette variable most closely matching the token category.


| Token | BSL | SDBL | CSS class | Color var |
| --- | --- | --- | --- | --- |
| `Comment` | :material-close: | :material-close: | `c` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Comment.Hashbang` | :material-close: | :material-close: | `ch` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Comment.Multiline` | :material-close: | :material-close: | `cm` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Comment.Preproc` | :material-check: | :material-close: | `cp` | <span class="twemoji" style="color: var(--md-code-hl-special-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-special-color` |
| `Comment.PreprocFile` | :material-close: | :material-close: | `cpf` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Comment.Single` | :material-check: | :material-check: | `c1` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Comment.Special` | :material-close: | :material-close: | `cs` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Error` | :material-close: | :material-close: | `err` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Escape` | :material-close: | :material-close: | `esc` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Generic` | :material-close: | :material-close: | `g` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Generic.Deleted` | :material-close: | :material-close: | `gd` | <span class="twemoji" style="color: var(--md-typeset-del-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-typeset-del-color (background)` |
| `Generic.Emph` | :material-close: | :material-close: | `ge` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.EmphStrong` | :material-close: | :material-close: | `ges` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Generic.Error` | :material-check: | :material-check: | `gr` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Heading` | :material-close: | :material-close: | `gh` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Inserted` | :material-close: | :material-close: | `gi` | <span class="twemoji" style="color: var(--md-typeset-ins-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-typeset-ins-color (background)` |
| `Generic.Output` | :material-close: | :material-close: | `go` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Prompt` | :material-close: | :material-close: | `gp` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Strong` | :material-close: | :material-close: | `gs` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Subheading` | :material-close: | :material-close: | `gu` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Generic.Traceback` | :material-close: | :material-close: | `gt` | <span class="twemoji" style="color: var(--md-code-hl-generic-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-generic-color` |
| `Keyword` | :material-check: | :material-close: | `k` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Keyword.Constant` | :material-check: | :material-check: | `kc` | <span class="twemoji" style="color: var(--md-code-hl-name-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-name-color` |
| `Keyword.Declaration` | :material-check: | :material-check: | `kd` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Keyword.Namespace` | :material-close: | :material-close: | `kn` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Keyword.Pseudo` | :material-close: | :material-close: | `kp` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Keyword.Reserved` | :material-close: | :material-close: | `kr` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Keyword.Type` | :material-close: | :material-close: | `kt` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Literal` | :material-close: | :material-close: | `l` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.Date` | :material-check: | :material-close: | `ld` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Literal.Number` | :material-check: | :material-check: | `m` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Bin` | :material-close: | :material-close: | `mb` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Float` | :material-close: | :material-close: | `mf` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Hex` | :material-close: | :material-close: | `mh` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Integer` | :material-close: | :material-close: | `mi` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Integer.Long` | :material-close: | :material-close: | `il` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.Number.Oct` | :material-close: | :material-close: | `mo` | <span class="twemoji" style="color: var(--md-code-hl-number-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-number-color` |
| `Literal.String` | :material-check: | :material-check: | `s` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Affix` | :material-close: | :material-close: | `sa` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Literal.String.Backtick` | :material-close: | :material-close: | `sb` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Char` | :material-close: | :material-close: | `sc` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Delimiter` | :material-close: | :material-close: | `dl` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Literal.String.Doc` | :material-close: | :material-close: | `sd` | <span class="twemoji" style="color: var(--md-code-hl-comment-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-comment-color` |
| `Literal.String.Double` | :material-close: | :material-close: | `s2` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Escape` | :material-check: | :material-check: | `se` | <span class="twemoji" style="color: var(--md-code-hl-special-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-special-color` |
| `Literal.String.Heredoc` | :material-close: | :material-close: | `sh` | <span class="twemoji" style="color: var(--md-code-hl-special-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-special-color` |
| `Literal.String.Interpol` | :material-check: | :material-check: | `si` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Other` | :material-close: | :material-close: | `sx` | <span class="twemoji" style="color: var(--md-code-hl-special-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-special-color` |
| `Literal.String.Regex` | :material-close: | :material-close: | `sr` | <span class="twemoji" style="color: var(--md-code-hl-special-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-special-color` |
| `Literal.String.Single` | :material-close: | :material-close: | `s1` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Literal.String.Symbol` | :material-close: | :material-close: | `ss` | <span class="twemoji" style="color: var(--md-code-hl-string-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-string-color` |
| `Name` | :material-close: | :material-close: | `n` | <span class="twemoji" style="color: var(--md-code-hl-name-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-name-color` |
| `Name.Attribute` | :material-check: | :material-close: | `na` | <span class="twemoji" style="color: var(--md-code-hl-variable-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-variable-color` |
| `Name.Builtin` | :material-check: | :material-check: | `nb` | <span class="twemoji" style="color: var(--md-code-hl-constant-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-constant-color` |
| `Name.Builtin.Pseudo` | :material-close: | :material-close: | `bp` | <span class="twemoji" style="color: var(--md-code-hl-constant-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-constant-color` |
| `Name.Class` | :material-check: | :material-check: | `nc` | <span class="twemoji" style="color: var(--md-code-hl-function-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-function-color` |
| `Name.Constant` | :material-close: | :material-close: | `no` | <span class="twemoji" style="color: var(--md-code-hl-constant-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-constant-color` |
| `Name.Decorator` | :material-check: | :material-close: | `nd` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Name.Entity` | :material-close: | :material-close: | `ni` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Name.Exception` | :material-check: | :material-close: | `ne` | <span class="twemoji" style="color: var(--md-code-hl-function-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-function-color` |
| `Name.Function` | :material-check: | :material-check: | `nf` | <span class="twemoji" style="color: var(--md-code-hl-function-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-function-color` |
| `Name.Function.Magic` | :material-close: | :material-close: | `fm` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Name.Label` | :material-check: | :material-close: | `nl` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Name.Namespace` | :material-check: | :material-check: | `nn` | <span class="twemoji" style="color: var(--md-code-hl-function-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-function-color` |
| `Name.Other` | :material-close: | :material-close: | `nx` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Name.Property` | :material-close: | :material-close: | `py` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Name.Tag` | :material-close: | :material-close: | `nt` | <span class="twemoji" style="color: var(--md-code-hl-keyword-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-keyword-color` |
| `Name.Variable` | :material-check: | :material-check: | `nv` | <span class="twemoji" style="color: var(--md-code-hl-variable-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-variable-color` |
| `Name.Variable.Class` | :material-close: | :material-close: | `vc` | <span class="twemoji" style="color: var(--md-code-hl-variable-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-variable-color` |
| `Name.Variable.Global` | :material-close: | :material-close: | `vg` | <span class="twemoji" style="color: var(--md-code-hl-variable-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-variable-color` |
| `Name.Variable.Instance` | :material-close: | :material-close: | `vi` | <span class="twemoji" style="color: var(--md-code-hl-variable-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-variable-color` |
| `Name.Variable.Magic` | :material-close: | :material-close: | `vm` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Operator` | :material-check: | :material-check: | `o` | <span class="twemoji" style="color: var(--md-code-hl-operator-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-operator-color` |
| `Operator.Word` | :material-close: | :material-close: | `ow` | <span class="twemoji" style="color: var(--md-code-hl-operator-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-operator-color` |
| `Other` | :material-close: | :material-close: | `x` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Punctuation` | :material-check: | :material-check: | `p` | <span class="twemoji" style="color: var(--md-code-hl-punctuation-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-hl-punctuation-color` |
| `Punctuation.Marker` | :material-close: | :material-close: | `pm` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Text` | :material-check: | :material-check: | `-` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
| `Text.Whitespace` | :material-close: | :material-close: | `w` | <span class="twemoji" style="color: var(--md-code-fg-color);"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12 2A10 10 0 0 0 2 12a10 10 0 0 0 10 10 10 10 0 0 0 10-10A10 10 0 0 0 12 2"/></svg></span> `--md-code-fg-color` |
