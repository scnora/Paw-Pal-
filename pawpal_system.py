from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


# ─────────────────────────────────────────────
#  Enum
# ─────────────────────────────────────────────

class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    VET_VISIT = "vet_visit"
    OTHER = "other"


# ─────────────────────────────────────────────
#  Dataclasses  (pure data — no complex logic)
# ─────────────────────────────────────────────

@dataclass
class Task:
    name: str
    task_type: TaskType
    duration_minutes: int
    priority: int                        # 1 (low) → 5 (critical)
    preferred_time: str = "anytime"      # "morning" | "afternoon" | "evening" | "anytime"
    notes: str = ""
    frequency: str = "daily"             # "daily" | "weekly" | "as-needed"
    is_completed: bool = False
    scheduled_time: str | None = None
    due_date: date = field(default_factory=date.today)

    def complete(self):
        """Mark this task as done."""
        self.is_completed = True

    def reschedule(self, new_time: str):
        """Move this task to a new time slot."""
        self.scheduled_time = new_time

    def get_priority_label(self) -> str:
        """Return a human-readable priority string (e.g. 'High')."""
        labels = {1: "Low", 2: "Low-Medium", 3: "Medium", 4: "High", 5: "Critical"}
        return labels.get(self.priority, "Unknown")

    def next_occurrence(self) -> "Task | None":
        """Return a fresh copy of this task due on its next occurrence, or None if non-recurring.

        Uses timedelta to calculate the next due_date: +1 day for "daily" tasks,
        +7 days for "weekly" tasks. Returns None for "as-needed" tasks, which
        do not auto-recur. The returned Task is a new instance with is_completed
        reset to False and scheduled_time cleared.
        """
        if self.frequency == "daily":
            next_due = self.due_date + timedelta(days=1)
        elif self.frequency == "weekly":
            next_due = self.due_date + timedelta(weeks=1)
        else:
            return None  # "as-needed" tasks do not auto-recur

        return Task(
            name=self.name,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            preferred_time=self.preferred_time,
            notes=self.notes,
            frequency=self.frequency,
            due_date=next_due,
        )


@dataclass
class Pet:
    name: str
    species: str                         # e.g. "dog", "cat"
    breed: str
    age: int                             # age in years
    tasks: list[Task] = field(default_factory=list)
    medical_conditions: list[str] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task by name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return self.tasks

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first."""
        return sorted(self.tasks, key=lambda t: t.priority, reverse=True)

    def get_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        return [t for t in self.tasks if not t.is_completed]

    def go_on_walk(self, duration_minutes: int = 30) -> Task:
        """Create a WALK task, add it to this pet, and return it."""
        walk = Task(
            name=f"{self.name}'s Walk",
            task_type=TaskType.WALK,
            duration_minutes=duration_minutes,
            priority=4,
            preferred_time="morning",
        )
        self.add_task(walk)
        return walk

    def add_medical_condition(self, condition: str):
        """Record a medical condition that may affect scheduling."""
        self.medical_conditions.append(condition)

    def clear_completed_tasks(self):
        """Remove all tasks marked as completed from this pet's task list."""
        self.tasks = [t for t in self.tasks if not t.is_completed]


@dataclass
class ScheduledTask:
    """A Task that has been assigned a time slot with an explanation."""
    task: Task
    scheduled_time: str
    pet: Pet                             # full Pet reference instead of just a name string
    reason: str                          # why the scheduler chose this slot

    @property
    def pet_name(self) -> str:
        """Convenience accessor so display code can still use .pet_name."""
        return self.pet.name


# ─────────────────────────────────────────────
#  Regular classes  (contain behaviour/logic)
# ─────────────────────────────────────────────

class Owner:
    def __init__(self, name: str, email: str = "",
                 available_minutes_per_day: int = 120):
        self.name = name
        self.email = email
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences: dict = {}      # e.g. {"walk_time": "morning"}
        self.pets: list[Pet] = []
        self._scheduler: "Scheduler | None" = None

    def add_pet(self, pet: Pet):
        """Register a pet under this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def set_available_time(self, minutes: int):
        """Update how many minutes per day are available for pet care."""
        self.available_minutes_per_day = minutes

    def set_preference(self, key: str, value):
        """Store an owner preference (e.g. set_preference('walk_time', 'morning'))."""
        self.preferences[key] = value

    def get_schedule(self) -> list[ScheduledTask]:
        """Generate and return today's schedule via the Scheduler."""
        if self._scheduler is None:
            self._scheduler = Scheduler(self)
        return self._scheduler.generate_daily_plan()

    def add_event_to_schedule(self, task: Task, pet: Pet):
        """Add a one-off task to a pet and regenerate the schedule, creating the Scheduler if needed."""
        pet.add_task(task)
        if self._scheduler is None:
            self._scheduler = Scheduler(self)
        self._scheduler.generate_daily_plan()

    def get_all_tasks(self) -> list[tuple[Task, Pet]]:
        """Return every task across all pets as (task, pet) pairs."""
        return [(task, pet) for pet in self.pets for task in pet.tasks]

    def get_all_pending_tasks(self) -> list[tuple[Task, Pet]]:
        """Return every incomplete task across all pets as (task, pet) pairs."""
        return [(task, pet) for pet in self.pets for task in pet.get_pending_tasks()]


class Scheduler:
    TIME_SLOTS = [
        "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00",
        "17:00", "18:00", "19:00", "20:00",
    ]

    TIME_OF_DAY_MAP = {
        "morning":   ["07:00", "08:00", "09:00", "10:00"],
        "afternoon": ["11:00", "12:00", "13:00", "14:00", "15:00"],
        "evening":   ["16:00", "17:00", "18:00", "19:00", "20:00"],
        "anytime":   ["07:00", "08:00", "09:00", "10:00", "11:00",
                      "12:00", "13:00", "14:00", "15:00", "16:00",
                      "17:00", "18:00", "19:00", "20:00"],
    }

    # Bump priority by this amount when a pet has medical conditions
    MEDICAL_PRIORITY_BOOST = 1

    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: list[ScheduledTask] = []
        self.total_scheduled_minutes: int = 0

    def generate_daily_plan(self) -> list[ScheduledTask]:
        """Collect all pending tasks, sort by priority, slot into free time windows, and return a time-ordered schedule."""
        self.reset_plan()
        used_slots: set[str] = set()

        # Gather all pending (task, pet) pairs
        all_tasks: list[tuple[Task, Pet]] = self.owner.get_all_pending_tasks()

        # Apply medical boost before sorting
        for task, pet in all_tasks:
            if pet.medical_conditions and task.task_type == TaskType.MEDICATION:
                task.priority = min(5, task.priority + self.MEDICAL_PRIORITY_BOOST)

        # Sort by priority descending so critical tasks are scheduled first
        prioritized = self._prioritize_tasks(all_tasks)

        for task, pet in prioritized:
            if not self._check_time_constraints(task):
                continue  # not enough time left today — skip

            slot = self._find_slot(task, used_slots)
            if slot is None:
                continue  # no free slot available — skip

            used_slots.add(slot)
            task.scheduled_time = slot
            reason = self._build_reason(task, pet)
            self.daily_plan.append(ScheduledTask(task, slot, pet, reason))
            self.total_scheduled_minutes += task.duration_minutes

        # Return plan in chronological order
        self.daily_plan.sort(key=lambda st: st.scheduled_time)
        return self.daily_plan

    def explain_plan(self) -> str:
        """Return a human-readable summary of the daily plan with reasoning."""
        if not self.daily_plan:
            return "No schedule generated yet. Call generate_daily_plan() first."

        lines = [
            f"Daily plan for {self.owner.name}",
            f"Time budget: {self.total_scheduled_minutes} / "
            f"{self.owner.available_minutes_per_day} min used\n",
        ]
        for st in self.daily_plan:
            lines.append(
                f"  {st.scheduled_time}  [{st.pet_name}]  {st.task.name}"
                f"  ({st.task.duration_minutes} min, {st.task.get_priority_label()} priority)"
                f"\n           Reason: {st.reason}"
            )
        return "\n".join(lines)

    def mark_task_complete(self, scheduled_task: ScheduledTask) -> "Task | None":
        """Mark a scheduled task done and queue the next occurrence for recurring tasks.

        Calls task.complete(), then uses task.next_occurrence() to create a fresh
        Task due tomorrow (daily) or in one week (weekly) and adds it back to the
        pet so the next call to generate_daily_plan() picks it up automatically.
        Returns the new Task if one was created, otherwise None.
        """
        scheduled_task.task.complete()
        next_task = scheduled_task.task.next_occurrence()
        if next_task is not None:
            scheduled_task.pet.add_task(next_task)
        return next_task

    def detect_conflicts(self) -> list[str]:
        """Scan the daily plan for tasks sharing the same time slot and return warning strings.

        Groups every ScheduledTask by its scheduled_time. Any slot that contains
        more than one task is a conflict. Returns a list of human-readable warning
        strings (one per conflict slot) — never raises, never modifies the plan.
        """
        # Group tasks by time slot using a plain dict — no imports needed
        slots: dict[str, list[ScheduledTask]] = {}
        for st in self.daily_plan:
            slots.setdefault(st.scheduled_time, []).append(st)

        warnings = []
        for time_slot, entries in sorted(slots.items()):
            if len(entries) > 1:
                names = " / ".join(
                    f"{e.task.name} ({e.pet_name})" for e in entries
                )
                warnings.append(
                    f"WARNING  {time_slot}  — {len(entries)} tasks overlap: {names}"
                )
        return warnings

    def sort_by_time(self) -> list[ScheduledTask]:
        """Return the daily plan sorted chronologically by scheduled time.

        Uses a lambda key on task.scheduled_time, which is a zero-padded "HH:MM"
        string — lexicographic order equals chronological order for this format.
        Does not modify self.daily_plan; returns a new sorted list.
        """
        return sorted(self.daily_plan, key=lambda st: st.task.scheduled_time)

    def filter_by_pet(self, pet_name: str) -> list[ScheduledTask]:
        """Return only the scheduled tasks that belong to the named pet.

        Filters self.daily_plan by comparing pet_name (case-sensitive) against
        each ScheduledTask's pet_name property. Returns an empty list if no tasks
        match — never raises. Does not modify the plan.
        """
        return [st for st in self.daily_plan if st.pet_name == pet_name]

    def filter_by_completion(self, completed: bool) -> list[ScheduledTask]:
        """Return scheduled tasks whose completion status matches the given flag.

        Pass completed=True for tasks already marked done, or completed=False
        for tasks still pending. Reads task.is_completed on the underlying Task.
        Returns an empty list if none match — never raises. Does not modify the plan.
        """
        return [st for st in self.daily_plan if st.task.is_completed == completed]

    # ── private helpers ──────────────────────────────────────────────────────

    def _find_slot(self, task: Task, used_slots: set[str]) -> str | None:
        """Return the earliest free slot matching the task's preferred time, falling back to any open slot."""
        preferred = (
            self.owner.preferences["walk_time"]
            if task.task_type == TaskType.WALK and "walk_time" in self.owner.preferences
            else task.preferred_time
        )
        # dict.fromkeys preserves insertion order while deduplicating:
        # preferred slots come first, remaining TIME_SLOTS fill in the fallback.
        candidates = dict.fromkeys(
            self.TIME_OF_DAY_MAP.get(preferred, self.TIME_SLOTS) + self.TIME_SLOTS
        )
        return next((slot for slot in candidates if slot not in used_slots), None)

    def _build_reason(self, task: Task, pet: Pet) -> str:
        """Construct a short explanation for why a task was scheduled when it was."""
        reasons = []

        if task.priority == 5:
            reasons.append("critical priority — must not be skipped")
        elif task.priority == 4:
            reasons.append("high priority")

        if task.task_type == TaskType.MEDICATION:
            reasons.append("medication task")
            if pet.medical_conditions:
                reasons.append(f"pet has condition(s): {', '.join(pet.medical_conditions)}")

        if task.preferred_time != "anytime":
            reasons.append(f"preferred {task.preferred_time} window")

        if task.frequency == "daily":
            reasons.append("recurring daily task")

        if not reasons:
            reasons.append("fits within available time budget")

        return "; ".join(reasons)

    def _prioritize_tasks(
        self, tasks: list[tuple[Task, Pet]]
    ) -> list[tuple[Task, Pet]]:
        """Sort (task, pet) pairs by priority descending, breaking ties by shortest duration first."""
        return sorted(tasks, key=lambda tp: (-tp[0].priority, tp[0].duration_minutes))

    def _check_time_constraints(self, task: Task) -> bool:
        """Return True if adding this task still fits within the owner's available time."""
        return (self.total_scheduled_minutes + task.duration_minutes
                <= self.owner.available_minutes_per_day)

    def reset_plan(self):
        """Clear the current daily plan and reset the scheduled minutes counter."""
        self.daily_plan = []
        self.total_scheduled_minutes = 0
