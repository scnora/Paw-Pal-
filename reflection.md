# PawPal+ Project Reflection

## 1. System Design
-- Sarai --
three core actions: add a pet, schedule event, did the pet eat, walk, meds, etc

attributes: pet type, breed, age, name, 
methods: go on walk, takemeds, addevent, getschedule


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial design of the UML is a easy way to take all the pet's needs and builds a daily schedule for the owner based on the time and priorities. The classes I have are Owner, Pet, Task, Scheduler, and ScheduledTask. The owner has a pet and pet can have 0 or more tasks. The scheduler plans for the owner and produces a ScheduledTask which then gives these Tasks to the pet. 


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

I did make some design changes during implementation. I changed the TIME_OF_DAY_MAP to prevents a runtime error by inlining values, and the add_event_to_schedule docstring shows expected behavior when no scheduler exists. I also made some improvements like changing ScheduledTask.pet_name to a Pet reference and adding a frequency field to Task ensure data stays consistent and supports recurring scheduling. Finally, clear_completed_tasks() and reset_plan() were added to prevent data buildup and duplication, keeping the system clean across multiple scheduling runs.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers the owner’s available time, task priority, and preferred time of day. I prioritized these because they reflect how people actually plan pet tasks like feeding or medication need to happen first, and everything has to fit within the time the owner realistically has. I didn’t focus as much on exact timing precision since most pet tasks are flexible within a general time window.


**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that it only checks for conflicts at the time slot level instead of comparing actual task durations. For example, two tasks assigned “09:00” would conflict, but a 60-minute task at 09:00 and a 30-minute task at 09:30 wouldn’t be flagged. This is reasonable because pet care tasks are usually short and routine, so people think of them in broad time blocks rather than exact overlapping minutes, and this keeps the system simpler without hurting usability.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
