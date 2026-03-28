from pawpal_system import Pet, Task, TaskType


def test_task_completion():
    """Calling complete() should flip is_completed from False to True."""
    task = Task(
        name="Morning Medication",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=5,
    )

    assert task.is_completed is False  # starts incomplete
    task.complete()
    assert task.is_completed is True   # flipped after complete()


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Mochi", species="dog", breed="Shiba Inu", age=3)

    assert len(pet.tasks) == 0  # starts with no tasks

    pet.add_task(Task(
        name="Morning Walk",
        task_type=TaskType.WALK,
        duration_minutes=20,
        priority=4,
    ))

    assert len(pet.tasks) == 1  # one task added
