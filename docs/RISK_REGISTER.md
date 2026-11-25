# Risk register

| Risk | Mitigation / status |
|---|---|
| Unsourced agronomic rule could mislead | Demo flags only; no treatment/dosage; require sourced review before operational advice |
| No local weather ground truth | Prototype uses no real forecast; later report proxy evaluation separately |
| LLM invents advice | Prompt constraints, character validator, fallback; grounding corpus not yet implemented |
| Provider timeout | 8-second timeout and deterministic fallback |
| Privacy | Synthetic records only; production consent, encryption and security remain unimplemented |
| GSM-7 validation incomplete | Prototype checker; verify provider encoding and multipart behavior before delivery |
| Scope growth | Frozen MVP scope and change log |
| Poor Swahili quality | Human review required; templates not yet rated |
| Telecom demo failure | Simulated SMS/USSD interfaces; provider integration deferred |
