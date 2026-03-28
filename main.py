from datetime import date
from pawpal_system import Owner, Pet, Task, TaskType

# ── Helper ────────────────────────────────────────────────────────────────────
def print_scheduled_tasks(label: str, scheduled_tasks):
    print(f"\n  {label}")
    if not scheduled_tasks:
        print("    (none)")
        return
    for st in scheduled_tasks:
        status = "DONE" if st.task.is_completed else "pending"
        print(f"    {st.scheduled_time}  [{st.pet_name}]  {st.task.name}"
              f"  ({st.task.get_priority_label()}, {status})")

# ── Owner & Pets ──────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", email="jordan@email.com", available_minutes_per_day=180)
jordan.set_preference("walk_time", "morning")

mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
mochi.add_medical_condition("arthritis")

luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)

jordan.add_pet(mochi)
jordan.add_pet(luna)

# ── Tasks added OUT OF ORDER (evening first, then morning) ────────────────────
luna.add_task(Task(
    name="Luna's Evening Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=10,
    priority=4,
    preferred_time="evening",
    frequency="daily",
))

luna.add_task(Task(
    name="Luna's Enrichment Play",
    task_type=TaskType.ENRICHMENT,
    duration_minutes=20,
    priority=3,
    preferred_time="evening",
    notes="Feather wand or puzzle feeder",
    frequency="daily",
))

mochi.add_task(Task(
    name="Mochi's Grooming",
    task_type=TaskType.GROOMING,
    duration_minutes=25,
    priority=2,
    preferred_time="afternoon",
    frequency="weekly",
))

mochi.add_task(Task(                        # added last — but highest priority
    name="Mochi's Joint Medication",
    task_type=TaskType.MEDICATION,
    duration_minutes=5,
    priority=5,
    preferred_time="morning",
    notes="Give with food",
    frequency="daily",
))

luna.add_task(Task(
    name="Luna's Morning Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=10,
    priority=4,
    preferred_time="morning",
    frequency="daily",
))

mochi.go_on_walk(duration_minutes=20)       # added last — morning walk shortcut

# ── Generate schedule ─────────────────────────────────────────────────────────
print("=" * 55)
print("           PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 55)

schedule = jordan.get_schedule()
scheduler = jordan._scheduler

for st in schedule:
    print(f"\n  {st.scheduled_time}  |  {st.task.name}")
    print(f"           Pet      : {st.pet_name}")
    print(f"           Type     : {st.task.task_type.value}")
    print(f"           Duration : {st.task.duration_minutes} min")
    print(f"           Priority : {st.task.get_priority_label()}")
    print(f"           Reason   : {st.reason}")

# ── Mark two tasks complete to test completion filter ─────────────────────────
# ── Recurrence demo via mark_task_complete() ─────────────────────────────────
# Use the scheduler method instead of calling .complete() directly so the
# next occurrence is automatically created and queued on the pet.
next_task_1 = scheduler.mark_task_complete(schedule[0])   # Mochi's Medication (daily)
next_task_2 = scheduler.mark_task_complete(schedule[1])   # Luna's Morning Feeding (daily)

# ── Sort & Filter demos ───────────────────────────────────────────────────────
print("\n" + "=" * 55)
print("  SORTING & FILTERING DEMOS")
print("=" * 55)

print_scheduled_tasks(
    "sort_by_time() — all tasks in chronological order:",
    scheduler.sort_by_time(),
)

print_scheduled_tasks(
    "filter_by_pet('Mochi') — only Mochi's tasks:",
    scheduler.filter_by_pet("Mochi"),
)

print_scheduled_tasks(
    "filter_by_pet('Luna') — only Luna's tasks:",
    scheduler.filter_by_pet("Luna"),
)

print_scheduled_tasks(
    "filter_by_completion(completed=True) — tasks already done:",
    scheduler.filter_by_completion(completed=True),
)

print_scheduled_tasks(
    "filter_by_completion(completed=False) — tasks still pending:",
    scheduler.filter_by_completion(completed=False),
)

print("\n" + "=" * 55)

# ── Conflict detection demo ───────────────────────────────────────────────────
# generate_daily_plan() never double-books a slot, so we inject two tasks
# manually at the same time to simulate a conflict and verify the detector.
print("  CONFLICT DETECTION DEMO")
print("=" * 55)

from pawpal_system import ScheduledTask  # noqa: E402 — import here for clarity

clash_task_1 = Task(
    name="Surprise Vet Visit",
    task_type=TaskType.VET_VISIT,
    duration_minutes=60,
    priority=5,
    preferred_time="morning",
    frequency="as-needed",
)
clash_task_1.scheduled_time = "09:00"

clash_task_2 = Task(
    name="Emergency Grooming",
    task_type=TaskType.GROOMING,
    duration_minutes=30,
    priority=3,
    preferred_time="morning",
    frequency="as-needed",
)
clash_task_2.scheduled_time = "09:00"   # ← same slot as clash_task_1

# Force both into the plan so detect_conflicts() has something to find
scheduler.daily_plan.append(ScheduledTask(clash_task_1, "09:00", mochi, "manually injected"))
scheduler.daily_plan.append(ScheduledTask(clash_task_2, "09:00", luna,  "manually injected"))

conflicts = scheduler.detect_conflicts()

if conflicts:
    print(f"\n  {len(conflicts)} conflict(s) found:\n")
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("\n  No conflicts detected.")

print("\n" + "=" * 55)

# ── Recurrence output ─────────────────────────────────────────────────────────
print("  RECURRENCE DEMO")
print("=" * 55)

today = date.today()
print(f"\n  Today's date : {today}")

for next_task in [next_task_1, next_task_2]:
    if next_task:
        days_away = (next_task.due_date - today).days
        print(f"\n  Completed    : {next_task.name}")
        print(f"  Frequency    : {next_task.frequency}")
        print(f"  Next due     : {next_task.due_date}  ({days_away} day(s) from today)")
        print(f"  How timedelta works:")
        print(f"    today ({today}) + timedelta(days=1) = {next_task.due_date}")

print("\n  Pending tasks now queued on each pet (ready for tomorrow's plan):")
for task, pet in jordan.get_all_pending_tasks():
    print(f"    [{pet.name}]  {task.name}  — due {task.due_date}")

print("\n" + "=" * 55)
