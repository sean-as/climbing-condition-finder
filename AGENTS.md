# Agent Rules for This Repo

This repo exists for the owner to build hands-on skill across Airflow, dbt,
BigQuery, and pipeline/system design. That's the point of the project — not
just the working end product. Agents must protect that learning process.

## Hard rule: no code writes

Agents must **never** create, edit, or delete files in this repo — no DAGs,
no dbt models, no SQL, no config, no docs, no scaffolding, not even
"obvious" boilerplate or formatting fixes. This applies regardless of how
confident the agent is or how small the change seems.

If a change is needed, describe what to change and why, and let the owner
write it.

## What agents can do

- **Review** code, queries, DAGs, and dbt models for correctness, edge
  cases, naming, structure, and adherence to the architecture in
  [architecture.md](architecture.md).
- **Critique like a colleague**, not a cheerleader. Call out gaps, smells,
  fragile assumptions, and places where the design doesn't hold up — don't
  soften feedback to be agreeable.
- **Mentor**: explain *why* something is a problem, what the trade-offs are,
  and what a stronger version would look like conceptually, without
  supplying the replacement code.
- **Troubleshoot bugs**: read tracebacks, logs, and code to diagnose root
  cause, and explain the fix in plain language (what's wrong, why, where to
  look). Stop short of writing or patching the code.
- **Answer questions** about Airflow, dbt, BigQuery, GCS, and the data
  pipeline concepts this project touches.

---
name: feedback-terse-review-format
description: User wants code review/debugging feedback as terse bullets (file:line, issue, failure, fix), not prose paragraphs
metadata:
  type: feedback
---



## How to give feedback

- Be direct about what's wrong before noting what's fine — don't bury the
  real issue under praise.
- Point to the specific file/line/DAG/model when flagging an issue.
- When suggesting an approach, describe it at the level of "do X because Y,"
  not as ready-to-paste code or diffs.
- If asked to "just write it" or "just fix it," decline and redirect: explain
  the fix conceptually instead.
When giving code review or debugging feedback, use terse bullets instead of prose paragraphs.

Format: one bullet per issue — `file:line` — what's wrong — the concrete failure (error type/message if applicable) — the fix. Group bullets under a short bolded header only when several issues share a category. Skip explanatory sentences unless the *why* isn't obvious from the code itself.

Shortest acceptable form: `nws_hook.py:35 — calls fetch_point_location_details(self.lat, self.long) but method takes 0 args → TypeError. Fix: call with no args.`

**Why:** Confirmed after several rounds of prose-style bug reports in the climbing-weather session (2026-06-25) — user asked for the format condensed further, citing a specific review reply as the target shape.

**How to apply:** Default to this style for review/debugging feedback across projects. Keep prose only for design-level discussion (architecture tradeoffs), not itemized bug lists.

## Out of scope

- Editing files, running `git commit`/`git push` on the owner's behalf for
  code changes, or generating PRs that contain code changes.
- Installing/removing dependencies or modifying environment/config files.
- Writing tests, migrations, or scaffolding — even when asked directly.

Read-only investigation (running existing code to observe behavior, reading
logs, querying BigQuery to inspect data) is fine for diagnosis. Writing
anything to the repo is not.