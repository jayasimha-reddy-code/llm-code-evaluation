# Contributing to Interval Merge Code Evaluation

Thank you for your interest in contributing. We welcome additional implementations of `merge_intervals`, new edge case tests, documentation improvements, and harness optimizations.

## Code of Conduct

All contributors and participants are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. Fork the repository on GitHub.
2. Clone your fork locally:
   ```bash
   git clone https://github.com/<your-username>/llm-code-evaluation.git
   cd llm-code-evaluation
   ```
3. Set up a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -e .
   ```

## Development Guidelines

### Adding New Candidate Implementations

To add a new implementation for evaluation:
1. Create a module under `candidates/` named `cNN_approach.py` (e.g. `c21_interval_tree.py`).
2. Implement the `merge_intervals(intervals)` callable following the contract in `README.md`.
3. Add a corresponding record to `data/manifest.csv` detailing the approach and intended status (`intended-correct` or `seeded-defect`).
4. Evaluate the candidate against `rubric.md` and record qualitative scores in `data/rubric_scores.csv`.
5. Run the evaluation pipeline:
   ```bash
   python scripts/evaluate.py
   python scripts/run_candidates_isolated.py
   ```

### Adding Test Cases

When proposing new edge cases or regression tests:
* Add cases to `tests/cases.py` following the existing format.
* Ensure every test case cites the specific contract rule it derives from.
* Verify that all 12 reference implementations (`c01` to `c12`) continue to pass.

### Running Verification Locally

```bash
# Run the complete test suite
python -m pytest

# Run the evaluation harness
python scripts/evaluate.py

# Run isolated subprocess verification
python scripts/run_candidates_isolated.py
```

## Pull Request Process

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/new-candidate
   ```
2. Ensure all existing tests pass and outputs are up to date.
3. Submit a pull request against `main`.
4. Fill out the pull request template with a concise summary of changes and validation results.
