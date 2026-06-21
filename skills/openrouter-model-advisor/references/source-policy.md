# Source Policy

Use sources in this order:

1. Live OpenRouter API data for current model IDs, prices, modalities, context length, supported parameters, expiration dates, and listed provider metadata.
2. Official provider documentation for durable capability descriptions and feature methods.
3. Benchmarks, leaderboards, and third-party evaluations for comparative quality signals.
4. Local project preferences for observed outcomes in this user's projects.

Separate fact types in the final explanation:

- Fact: directly from OpenRouter API or official docs.
- Inference: derived from price/capability matching.
- Evaluation: benchmark or local quality judgment.
- Preference: project-specific local observation.

Ask before action when:

- A premium model is recommended mainly for quality and a cheaper adequate model exists.
- The recommended model differs from the known current model for the project.
- The task could be satisfied by multiple plausible model families and the user did not state cost or quality priority.

Do not ask when:

- The user explicitly requested a specific model.
- The advisor selects a low-cost exploratory model and there is no project model switch.
- The project preference and current model already match the recommendation.

When unsure, present one concise recommendation and one cheaper alternative. Avoid long model catalogs unless the user asks for them.
