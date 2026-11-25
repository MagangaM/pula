# Prototype model card

## Intended use
Demonstrate a pipeline for a crop-context-aware advisory interface. Not for operational agronomic decisions.

## Components and methods
Manually selected stage and farmer-reported risk flags. Optional language generation via Groq chat-completions API. Deterministic template fallback. GSM-7 and length checks.

## Baseline
Deterministic template. No comparative performance claims are made.

## Data
Synthetic records and user-entered demo values only. No training data. No model training.

## Metrics
Prototype tests check character constraints and rule-path behavior. No agricultural accuracy metrics have been measured.

## Limitations and failure modes
No verified GDD, weather ingestion, source-grounded risk thresholds, RAG, field validation or expert rating. A generated advisory may still be incorrect or unclear.

## Must not be used for
Pesticide recommendations, disease diagnosis, operational irrigation scheduling, emergency decisions, or real farmer alerts.
