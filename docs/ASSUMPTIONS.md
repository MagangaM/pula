# Assumptions and validation plan

- The MVP's risk flags are manually supplied demo signals, not validated crop models. Validate each rule against verified KALRO/extension/CABI materials and expert review before use.
- Stage is manually selected; crop-specific GDD base temperatures and stage boundaries are not yet implemented. Obtain verified crop-specific sources and compare against field labels.
- Weather is not connected. Integrate a verified API and record provider, issue time, forecast horizon and retrieval time.
- Synthetic cohort is only for UI/demo testing. Never use as real participant data.
- LLM API is optional; endpoint/model and cost need verification. Template fallback is expected.
- The SMS check approximates GSM-7 character membership and single-message limits; test multipart behavior and telecom provider contract before deployment.
- Current regulatory and provider terms must be verified before M1/M5 integration.
