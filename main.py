from pawpal_system import Owner, Pet, Task, TaskType

# ── Create Owner ──────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", email="jordan@email.com", available_minutes_per_day=180)
jordan.set_preference("walk_time", "morning")

# ── Create Pets ───────────────────────────────────────────────────────────────
mochi = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)
mochi.add_medical_condition("arthritis")

luna = Pet(name="Luna", species="cat", breed="Siamese", age=5)

jordan.add_pet(mochi)
jordan.add_pet(luna)

# ── Add Tasks to Mochi ────────────────────────────────────────────────────────
mochi.go_on_walk(duration_minutes=20)  # shortcut — creates a morning WALK task

mochi.add_task(Task(
    name="Mochi's Joint Medication",
    task_type=TaskType.MEDICATION,
    duration_minutes=5,
    priority=5,
    preferred_time="morning",
    notes="Give with food",
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

# ── Add Tasks to Luna ─────────────────────────────────────────────────────────
luna.add_task(Task(
    name="Luna's Morning Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=10,
    priority=4,
    preferred_time="morning",
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

luna.add_task(Task(
    name="Luna's Evening Feeding",
    task_type=TaskType.FEEDING,
    duration_minutes=10,
    priority=4,
    preferred_time="evening",
    frequency="daily",
))

# ── Generate & Print Schedule ─────────────────────────────────────────────────
print("=" * 55)
print("           PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 55)

schedule = jordan.get_schedule()

for st in schedule:
    print(f"\n  {st.scheduled_time}  |  {st.task.name}")
    print(f"           Pet      : {st.pet_name}")
    print(f"           Type     : {st.task.task_type.value}")
    print(f"           Duration : {st.task.duration_minutes} min")
    print(f"           Priority : {st.task.get_priority_label()}")
    print(f"           Reason   : {st.reason}")

print("\n" + "=" * 55)
print(jordan._scheduler.explain_plan())
print("=" * 55)
