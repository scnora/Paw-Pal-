# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Smarter Scheduling

PawPal+ goes beyond a basic task list with several algorithmic features built into the `Scheduler` class:

**Conflict detection** — `detect_conflicts()` scans the daily plan for tasks that share the same time slot and returns a plain-English warning for each collision. It never raises an exception or modifies the schedule — the caller decides how to handle it.

**Chronological sorting** — `sort_by_time()` returns the daily plan ordered from earliest to latest using a lambda key on zero-padded `"HH:MM"` strings, where lexicographic order equals chronological order.

**Filtering** — `filter_by_pet(name)` and `filter_by_completion(bool)` let you slice the plan by pet or by done/pending status. Both are non-destructive and return new lists.

**Automatic recurrence** — `mark_task_complete()` calls `task.next_occurrence()` after marking a task done. For `"daily"` tasks it uses `timedelta(days=1)` to calculate tomorrow's due date; for `"weekly"` tasks it uses `timedelta(weeks=1)`. The new Task instance is automatically added back to the pet so the next call to `generate_daily_plan()` picks it up. `"as-needed"` tasks do not recur.

**Medical priority boost** — when a pet has a recorded medical condition, the scheduler automatically raises the priority of that pet's `MEDICATION` tasks (up to a max of 5) before sorting, so critical care is never pushed out by lower-priority activities.

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
