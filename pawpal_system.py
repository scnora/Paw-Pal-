from dataclasses import dataclass, field
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
    is_completed: bool = False
    scheduled_time: str | None = None

    def complete(self):
        """Mark this task as done."""
        pass

    def reschedule(self, new_time: str):
        """Move this task to a new time slot."""
        pass

    def get_priority_label(self) -> str:
        """Return a human-readable priority string (e.g. 'High')."""
        pass


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
        pass

    def remove_task(self, task_name: str):
        """Remove a task by name."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        pass

    def get_tasks_by_priority(self) -> list[Task]:
        """Return tasks sorted highest priority first."""
        pass

    def get_pending_tasks(self) -> list[Task]:
        """Return only incomplete tasks."""
        pass

    def go_on_walk(self, duration_minutes: int = 30) -> Task:
        """Create a WALK task, add it to this pet, and return it."""
        pass

    def add_medical_condition(self, condition: str):
        """Record a medical condition that may affect scheduling."""
        pass


@dataclass
class ScheduledTask:
    """A Task that has been assigned a time slot with an explanation."""
    task: Task
    scheduled_time: str
    pet_name: str
    reason: str                          # why the scheduler chose this slot


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
        pass

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        pass

    def set_available_time(self, minutes: int):
        """Update how many minutes per day are available for pet care."""
        pass

    def set_preference(self, key: str, value):
        """Store an owner preference (e.g. set_preference('walk_time', 'morning'))."""
        pass

    def get_schedule(self) -> list[ScheduledTask]:
        """Generate and return today's schedule via the Scheduler."""
        pass

    def add_event_to_schedule(self, task: Task, pet: Pet):
        """Add a one-off task to a pet and regenerate the schedule."""
        pass


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
        "anytime":   TIME_SLOTS,
    }

    def __init__(self, owner: Owner):
        self.owner = owner
        self.daily_plan: list[ScheduledTask] = []
        self.total_scheduled_minutes: int = 0

    def generate_daily_plan(self) -> list[ScheduledTask]:
        """
        Build a daily schedule for all of the owner's pets.
        Sort tasks by priority, slot them into available time windows,
        and return a time-ordered list of ScheduledTasks.
        """
        pass

    def explain_plan(self) -> str:
        """Return a human-readable summary of the daily plan with reasoning."""
        pass

    def _find_slot(self, task: Task, used_slots: set[str]) -> str | None:
        """Return the earliest free slot that matches the task's preferred time."""
        pass

    def _build_reason(self, task: Task) -> str:
        """Construct a short explanation for why a task was scheduled when it was."""
        pass

    def _prioritize_tasks(self, tasks: list[tuple[Task, Pet]]) -> list[tuple[Task, Pet]]:
        """Sort (task, pet) pairs by priority descending."""
        pass

    def _check_time_constraints(self, task: Task) -> bool:
        """Return True if adding this task still fits within the owner's available time."""
        pass
