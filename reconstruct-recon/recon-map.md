# Recon map: {{app}} ({{platform}})

Scope and mode: see `scope.md`. Mode {{A | B}}.
Date: {{YYYY-MM-DD}}

Every row below cites evidence: a source number from the table (tier A) or a
REA Evidence ID `ev_...` (tier B). Confidence is `observed`, `inferred` or
`guess`.

## Sources

| # | tier | source | URL or artifact | notes |
| --- | --- | --- | --- | --- |
| 1 | A | help center | | |
| 2 | B | REA analyze_javascript_application | ev_... | {{coverage limits}} |

## Core loop

{{one sentence: the thing users pay for}}

## Screens

| ID | screen | route / how to reach | purpose | key components | states seen | evidence | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S01 | | | | | empty, filled, error | 1 | observed |

## Flows

```
F01 {{goal}}
    S01 -> S02 -> S03
    happy path clicks: {{n}}
    edge: {{cases}}
    evidence: {{source numbers or ev_ IDs}}   confidence: {{observed | inferred | guess}}
```

## Components

| component | variants | states | used on |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, danger | default, hover, focus, disabled, loading | all |

## Data model

```
{{Entity}}  {{fields}}
            evidence: {{screen IDs, help articles, ev_ IDs}}
            confidence: observed | inferred | guess
```

Relationships: {{User 1-n EventType, EventType 1-n Booking, ...}}

## Feature matrix

See `features.csv`. Must: {{n}}, should: {{n}}, could: {{n}}, skip: {{n}}.
Evidence: artifact {{n}}, public {{n}}, none {{n}}.

## Unknowns

| question | why it matters | next probe | REA unknown ID |
| --- | --- | --- | --- |

## Out of scope (cannot or should not be rebuilt)

- {{licensed content, the network, partner deals, ...}}

## Size

Screens {{n}}, flows {{n}}, entities {{n}}. Hard parts: {{list}}. Size: {{S|M|L|XL}}.
