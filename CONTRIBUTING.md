# Contributing to J.A.R.V.I.S.

Thank you for your interest in contributing to **J.A.R.V.I.S.**!

## Architecture Guidelines
- **Autonomous Core**: All LLM routing must navigate through OmniRoute on port `20128`.
- **Sub-500ms Audio SLA**: Any new voice additions must support flow-matching ODE with `num_step <= 2`.
- **Safe Execution**: All OS writes must respect the `--writes` flag.

