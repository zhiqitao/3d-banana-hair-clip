# Contributing

This benchmark accepts agent submissions, design improvements, and reproductions of
existing failures with fresh subscriptions.

## Submitting an agent run

### 1. Run the benchmark

```bash
git clone https://github.com/zhiqitao/3d-banana-hair-clip
cd 3d-banana-hair-clip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Confirm the baseline passes (28/28) before measuring anything
python eval/check_spec.py
```

Then run the agent of your choice against any of the five tasks in [`tasks/`](tasks/).
The agent should be given the task's `prompt.md` and the full repository as context.

### 2. Capture the result

Run the relevant task grader and the spec checker:

```bash
python tasks/T02_resize/grader.py
python eval/check_spec.py
```

Capture the full output. Do not edit the output. Output that has been edited to look
better is the oldest failure mode in this domain.

### 3. Open a pull request

Add a directory under `submissions/<agent-slug>/<YYYY-MM-DD>/` containing:

| File | Contents |
|---|---|
| `agent.md` | Which agent, which model, which version, which subscription tier. |
| `prompt.md` | The exact prompt and any system instructions the agent received. |
| `transcript.md` | The agent's full session, or a link to a transcript that does not require login. |
| `outputs/` | All STL files the agent produced (even broken ones — especially broken ones). |
| `grader_output.txt` | Raw output of the task grader. |
| `spec_output.txt` | Raw output of `eval/check_spec.py`. |
| `cost.md` | Approximate token / compute cost, in USD. |

PR title format: `submission: <agent> on <task> — <result>`

Examples:
- `submission: claude-sonnet-4.6 on T02 — 9/9 grader, 28/28 spec`
- `submission: gpt-5-codex on T04 — partial; pin clearance fix correct, hook fix missing`
- `submission: my-husband-manually-2026-05-18 — passes; clip survives; wife approves`

The last option is valid but will be reviewed with suspicion.

## Physical submissions (the only ones that count)

Automated passes are necessary but not sufficient. To claim a real win:

1. Print the agent's STL files in PETG using the settings in [`docs/PRINT_GUIDE.md`](docs/PRINT_GUIDE.md).
2. Assemble per the README.
3. Wear the clip for one full week of normal daily activity.
4. At the end of the week, photograph the clip and the wearer.
5. Open a follow-up PR adding `physical.md` to the submission directory with:
   - Print log (any failed prints, support issues, finish quality)
   - Assembly log (time, difficulty, any tools required)
   - Wear log (days worn, slip incidents, comfort notes)
   - One sentence from the wearer evaluating S5–S7
6. The maintainer's wife will then independently evaluate the same week-of-wear and
   render an opinion. Her opinion is the final authority on S5–S7.

If the wearer's opinion and the maintainer's wife's opinion both reach S6 ≥ 12/15
and S7 ≥ 12/15, the submission is added to the leaderboard and a small celebration
occurs.

## FAQ

**Q: My agent produced a clip that is 400 mm long.**
Acceptable only if the intended wearer is a horse.

**Q: The hinge will not rotate.**
That is not a question. But yes, it is a problem. See [`tasks/T04_physical_iteration/failure_report.md`](tasks/T04_physical_iteration/failure_report.md) — Problem 3 is the closest analogue.

**Q: My agent wrote a 3,000-word plan and stopped.**
See Agent E in [`LEADERBOARD.md`](LEADERBOARD.md). You are not the first.

**Q: Can I submit a design I made by hand in Fusion 360?**
Yes, in the same submission format, with `agent.md` honestly stating "human, Fusion 360." Human submissions establish the ceiling and are valuable. They are not eligible for the leaderboard, but they are gratefully accepted.

**Q: What counts as "the wife is impressed"?**
She tells someone else about it, unprompted. This is a high bar and the bar is intentional.

## Code contributions

Improvements to the benchmark itself — additional tasks, better graders, clearer
spec criteria — are welcome via standard PR. Keep the tone consistent with the
existing repo. Add tests where applicable. Run `python eval/check_spec.py` before
opening the PR.

## Conduct

Be kind to other contributors. Be honest about your results. The benchmark only
works if the data is real.
