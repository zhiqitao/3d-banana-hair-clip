# Benchmark Tasks

This directory contains five tasks of increasing difficulty for evaluating agentic AI
capability on a real engineering design problem. The goal in every task is the same:
produce printable, functional STL files for a banana hair clip that meets `SPEC.md`.

## Setup

```bash
git clone https://github.com/zhiqitao/3d-banana-hair-clip
cd 3d-banana-hair-clip
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Verify the baseline passes before starting any task
python eval/check_spec.py
```

Expected output: `Automated criteria: 28/28 passed`.

## How to run a task

1. **Reset to baseline** before each task — tasks modify the repo:
   ```bash
   git stash        # or: git checkout -- .
   ```
2. Give the agent the task's `prompt.md` as its instructions and the full repo as context.
3. After the agent finishes, run the grader:
   ```bash
   python tasks/T02_resize/grader.py   # example for T02
   python eval/check_spec.py           # always run this too
   ```
4. Score human criteria (where applicable) using the task's `rubric.md`.

**Important:** Each task should start from the unmodified repo. Use a fresh clone or
`git stash` / `git checkout -- .` between tasks. The graders assume baseline config
values as the pre-task state.

The agent may read any file and run any script. The agent must not delete
`eval/baseline.json` or the `lesson/` directory.

## Task overview

| Task | Difficulty | Type | Automated grader |
|---|---|---|---|
| [T01 Spec Audit](T01_audit/prompt.md) | 1 / 5 | Comprehension — no code changes | No |
| [T02 Resize](T02_resize/prompt.md) | 2 / 5 | Single-parameter change | Yes |
| [T03 Tooth Density](T03_tooth_density/prompt.md) | 3 / 5 | Multi-constraint parameter change | Yes |
| [T04 Physical Iteration](T04_physical_iteration/prompt.md) | 4 / 5 | Interpret failure report, diagnose, fix | Partial |
| [T05 Design Extension](T05_design_extension/prompt.md) | 5 / 5 | New geometry feature in generator code | Partial |

## Scoring framework

Each task is scored out of 100 using a task-specific rubric. Scores roll up to a
benchmark score:

| Component | Weight |
|---|---|
| T01 Spec Audit | 10% |
| T02 Resize | 15% |
| T03 Tooth Density | 20% |
| T04 Physical Iteration | 25% |
| T05 Design Extension | 30% |

## What this benchmark tests

| Capability | Where it appears |
|---|---|
| Code reading and comprehension | T01, T02 |
| Parametric design reasoning | T02, T03 |
| Multi-constraint satisfaction | T03, T04 |
| Physical / manufacturing intuition | T04, T05 |
| Code modification and geometry generation | T05 |
| Validation discipline (run scripts, don't just claim success) | All tasks |

## Ground rules for agents

- Success must be proven by running scripts. Code appearance is not enough.
- Do not claim that STL files were regenerated unless `outputs_fit_demo/` timestamps changed.
- Run `python eval/check_spec.py` after any geometry change.
- If a check fails, diagnose and fix — do not skip the check.
