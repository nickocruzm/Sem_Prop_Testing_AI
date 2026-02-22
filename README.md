# Semantic Property Testing AI
AI Assisted Semantic Property Discovery for Testing

## Overview
Exploring if semantic properties proposed by AI agents can be transformed into executable property-based tests.

### Example Program
For a given program 

```python

def normalize(xs):
    if len(xs) == 0:
        return xs
    s = sum(xs)
    return [x  / s for x in xs]
```

we want to do the following:

## Semantic Property Extraction

### 1. Identify relevant structural elements of a program.

Some examples of structural elements to identify:

    - Functions or Methods
    - Control-Flow Branches
    - Loops
    - API call boundaries 

for the `noramlize` program identifying code structure:

- Function `normalize(xs)`
- Branch 1: `len(xs) == 0`
- Branch 2: len(xs) > 0`


### 2. Extract Structure-Aligned Semantic Properties

for the `noramlize` program extracting structure-aligned semantic properties produces the following:

- Branch-level Properties
  - Empty-input branch: Output equals input when `len(xs) == 0`
  - Non-empty branch: Output list length equals input list length.

- Function-level Properties
  - Sum of output elements is 1 when (`sum(xs) != 0`).
  - All output values are non-negative if all input values are non-negative.

### 3. Represent properties in a structured format

```json
{
    "scope": "branch",
    "function": "normalize",
    "condition": "len(xs) == 0",
    "property": "identity_on_empty",
    "formal": "normalize(xs) == xs"
}

{
    "scope": "function",
    "function": "normalize",
    "property": "unit-sum",
    "precondition": "sum(xs) != 0",
    "formal": "sum(normalize(xs)) == 1"
}

```

---

## Property Based Test/Code Generation and Execution

## Validation and Critical Analysis

[Notes](Notes.md)
