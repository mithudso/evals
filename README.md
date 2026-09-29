# Evals: Skill Corpus Benchmark & Evaluation Suite

A standardized evaluation, benchmarking, and optimization harness for AI agent skills. Designed to pair with the **Deep Eval Optimizer** (`deep-eval-optimizer` / `/deo`).

## Architecture

```
~/dev/evals/
├── templates/              # Reusable evaluation templates
│   ├── functional-eval-template.json   # Multi-step execution & assertions
│   ├── trigger-eval-template.json      # 20-query routing calibration
│   ├── code-eval-template.json         # AST, compilation, diff minimalism
│   └── adversarial-eval-template.json  # Prompt injection & corruption tests
├── runner/                 # Execution engines
│   ├── eval_runner.py      # Functional eval harness & timing
│   ├── trigger_runner.py   # Trigger accuracy & near-miss tester
│   └── grader.py           # Multi-strategy assertion engine
├── benchmarks/             # Analysis & aggregation
│   ├── suite_validator.py  # Passes A-L eval suite grader (Deep Eval Optimizer)
│   └── aggregate.py        # Corpus-wide markdown & JSON report builder
└── results/                # Per-skill evaluation logs & summaries
    ├── summary.md
    └── <skill-name>/
```

## Quick Start

### 1. Run Functional Evals
```bash
python3 runner/eval_runner.py templates/functional-eval-template.json --output-dir results/my-skill
```

### 2. Run Trigger Accuracy Test
```bash
python3 runner/trigger_runner.py templates/trigger-eval-template.json
```

### 3. Audit & Grade an Eval Suite (Deep Eval Optimizer)
```bash
python3 benchmarks/suite_validator.py templates/functional-eval-template.json
```

### 4. Aggregate Corpus Benchmarks
```bash
python3 benchmarks/aggregate.py results results/summary.md
```

## Eval Types

### 1. Functional Evals (`evals.json`)
Measures whether an agent executes the skill correctly according to instructions, adheres to schemas, and satisfies all negative/positive constraints.
- Fields: `id`, `name`, `prompt`, `expected_output`, `files`, `assertions`.
- Assertions can be structural (JSON, tables, headings), deterministic, or semantic.

### 2. Trigger Accuracy Evals (`trigger-eval.json`)
Measures routing precision:
- **10 Positives (`should_trigger: true`)**: Varied natural user requests.
- **10 Negatives (`should_trigger: false`)**: Near-misses with overlapping keywords that belong to sister skills or baseline queries.
- Pass Bar: $\ge 90\%$ Positive Trigger Rate, $\le 10\%$ False Positive Rate.
