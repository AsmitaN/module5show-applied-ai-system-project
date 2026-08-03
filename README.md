# PawPal+ (Module 2 Project)

## Summary
Pawpal+ is a Streamlit app that lets multiple pet owners add/edit tasks, and view their schedule. They can choose to sort by datetime and apply different filters to view their schedule in a certain way. The AI feature I included is **Agentic Workflow**, and it is used after the "Add task" button is clicked.

## Features

- **Sorting by Time** — Tasks are automatically sorted by date and time, displaying them in chronological order across all pets
- **Conflict Warnings** — The system detects and prevents scheduling conflicts by warning when a task is assigned to the same time slot as an existing task
- **Daily/Weekly Recurrence** — Tasks marked as complete automatically advance to the next day/week, enabling recurring daily/weekly pet care activities
- **Filter by Pet/Status** — View tasks filtered by specific pet or completion status (pending/complete) for focused scheduling

## Architecture Overview
The architecture consists of classes falling into three distinct categories: Core Design, Scheduling & Conflict Management, and AI Integration Component. The Core Design consists of mostly everything that existed in the original layout, which are: Owner, Pet, and Task.\
The Owner class can add pets and create schedules. The Pet class can return pet-speific information. The Task class can be used to determine the priority level of the given task.\
The Scheduling & TaskFeedback topic contains the Scheduler and TaskValidator classes, where Scheduler manages schedules and TaskValidator finds scheduling conflicts and constructs tailored prompts to receive feedback from AI agent. \
The AI Integration Component theme includes only the GeminiClient class, which configures the Gemini client, then requests and receives information from the API.

## Setup Instructions
1) Activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```
2) Install dependencies\
`pip install -r requirements.txt`
3) Rename `.env.example` (located in project root) to `.env`
4) Visit the [Gemini API key page](https://aistudio.google.com/app/api-keys) and create your own key. Copy the key into your `.env` file 
5) Start the app
```bash 
python -m streamlit run app.py
```

## Sample Interactions
1) Adding task and there are no conflicts with existing tasks from any of the owner's pets.
```
Owner: Jordan, Pet: Mochi, Description: Walk, Duration: 30 minutes, Date: Today's or later, Frequency: Daily, Priority: high, Time to complete by: 09:00
AI Analysis
As a Golden Retriever, Mochi will certainly enjoy this daily morning walk! However, at 30 minutes, the duration is a bit short for an active, high-priority routine for this breed, which typically requires 60 to 90 minutes of daily exercise. Since the priority is set to "high," I suggest extending the walk to 45–60 minutes or adding some fetch and mental stimulation. Overall, it's a great foundational habit to keep Mochi healthy and happy!
```

2) Adding task but there is a conflict with existing task from same pet.
```
Owner: Jordan, Pet: Mochi, Description: Feeding, Duration: 10 minutes, Date: Same date as Mochi "Walk" task, Frequency: Daily, Priority: high, Time to complete by: 09:00
Hello! As Mochi's pet care scheduling assistant, I have analyzed the scheduling conflict for August 3, 2026.

Conflict Analysis
The Conflict: You are attempting to schedule Mochi's Feeding (High priority, 10 minutes, daily) at 09:00, which directly overlaps with her existing Walk (30 minutes) scheduled from 09:00 to 09:30.
Pet Health & Safety Considerations:
Critical Rule: Golden Retrievers (and large, deep-chested dog breeds) are at a high risk for Gastric Dilatation-Volvulus (GDV), commonly known as bloat. Strenuous exercise, such as a walk, immediately before or after a meal is a major trigger for GDV.
Therefore, Mochi must not eat right before her walk, nor should she go on an energetic walk immediately after eating. A resting/digestion window of at least 30 to 60 minutes is strongly recommended around feeding times.
Top 3 Recommended Alternative Times for Feeding
Since the 09:00–09:30 slot is locked down by her walk, here are the best alternative times to slot in her 10-minute daily feeding:

1. Recommended Time: 08:00 to 08:10 (1 hour before the walk)
Why: This is the safest and most biologically sound option. Feeding Mochi at 08:00 gives her a full hour to digest her food before her 09:00 walk. This completely eliminates the risk of bloat/GDV and ensures she has digested enough to have good energy for her walk without a heavy stomach.
2. Recommended Time: 09:30 to 09:40 (Immediately following the walk)
Why: If early morning feeding isn't preferred, feeding her right after the walk is acceptable provided the walk is low-intensity and you allow Mochi to cool down and catch her breath for 10–15 minutes inside before presenting her food. (Just ensure she doesn't gulp her food down frantically while still panting).
3. Recommended Time: 08:15 to 08:25 (45 minutes before the walk)
Why: This is a great middle-ground if 08:00 is too early for your morning routine. A 45-minute window provides a safe, adequate buffer for digestion before her physical activity begins at 09:00.
Final Assistant Recommendation:
Move Mochi's Feeding to 08:00 to 08:10. This protects her health, prevents the scheduling overlap, and maintains a healthy routine for her breed.
```
3) Adding task but there is a conflict with existing task from different pet.
```
Owner: Jordan, Pet: Bubble(breed: Goldfish), Description: Tank cleaning, Duration: 45 minutes, Date: Same date as Flora(Syrian Hamster) "Feeding" task, Frequency: Weekly, Priority: high, Time to complete by: 20:00
As a pet care scheduling assistant, I have analyzed the scheduling conflict involving Bubble's new tank cleaning task and Flora's existing feeding task on August 3, 2026, at 20:00.

Conflict Analysis
The Conflict: Bubble's daily Tank cleaning (high priority, 45 minutes, requested for 20:00) directly overlaps with Flora's Feeding (20:00 to 20:02).
Species Considerations:
Bubble (Goldfish): While daily tank cleaning is unusually frequent for a standard setup, maintaining water quality is critical for fish health. However, a 45-minute daily disruption to a goldfish's environment can cause chronic stress. That said, performing tank maintenance in the evening is generally acceptable as long as it doesn't disrupt sleep cycles by keeping lights on too late.
Flora: The feeding task is brief (2 minutes) but time-sensitive for routine.
Current Schedule Constraints: The occupied time slots for the day are 09:00 to 09:30 and 20:00 to 20:02.
Since Flora's feeding is brief and unmovable due to established routines, Bubble's tank cleaning must be rescheduled. Furthermore, performing a 45-minute cleaning right at 20:00 leaves little room before standard aquarium light-off times.

Top 3 Recommended Alternative Times for Bubble's Tank Cleaning
1. Recommended Alternative: 18:30 to 19:15 (Same Day)
Why: This slot places the cleaning just before the evening feeding routine (and the existing 20:00 conflict). It gives Bubble a clean environment well before nightfall, allowing the fish adequate time to calm down and settle before the aquarium lights are turned off for the night. It also completely avoids the busy 20:00 hour.
2. Recommended Alternative: 10:00 to 10:45 (Same Day)
Why: This utilizes the morning gap right after the 09:00–09:30 occupied slot. Morning cleanings are often ideal for aquatic pets because it aligns with daylight hours, natural biological rhythms, and gives the filter plenty of daytime hours to clear up any stirred-up debris before darkness.
3. Recommended Alternative: 19:15 to 20:00 (Same Day)
Why: This option places the cleaning session immediately before Flora's feeding at 20:00, utilizing the tail-end of the evening window. While it is tight against the 20:00 mark, it finishes right as Flora is being fed, keeping all pet-care duties consolidated into a neat evening block without overlapping. (Note: Ensure the cleaning wraps up strictly by 20:00 to avoid conflicting with Flora).
```

## Design Decisions
I built this system this way because I wanted to create a friendly interface that allows users to manage schedules as an owner of (potentially) various pets.\
I also decided to include multiple owners to account for the circumstance where pet sitters are forming schedules for pets of different owners.\
The application pre-populates owner and pet names as well as task descriptions so that the user can conveniently select the type whose value they want to edit.\
Example state changes include changing a task status and/or viewing the schedule for a particular pet of a an owner.\
Some of the main functionalities of the app are adding/editing tasks, sorting schedule by datetime, and filtering tasks by pet and completion_status.\
The AI agent is used to either explain and suggest alternative times for conflicting tasks (new vs existing) or provide a summary of optional changes to a non-conflicting new task.\
It also considers various factors such as breed-specific care, task priority and frequency, and the task's placement with respect to other tasks in the same due date.\
Something else to note is that recurring completed tasks are reset to pending only when today's date is the same as their upcoming due date.\
Some trade-offs of the design are that it currently can't sort tasks from highest to lowest priority (or vice versa) and the schedule across various days is not shown in a calendar display-format.

## Testing Summary
Automated testing (pytest) and human evaluation was performed to measure the system's reliability.\
6 out of 6 tests from `test_pawpal_applied_ai_system.py` passed, one of which included sending context to the Gemini API and receiving conflict analysis.\
Note, all `test_pawpal.py` tests fail because test my older version of Pawpal+. Instead, run all tests in `test_pawpal_applied_ai_system.py` to test the extended version of my project using the command below.

```bash
python -m pytest -v -s tests/test_pawpal_applied_ai_system.py
```

| Test Input | Evaluation Criteria | Result |
|------------|---------------------|--------|
| "Add button" clicked for task with one or more empty task-related input fields | Displays error and stops script execution | Pass |
| "Add button" clicked for task with conflicting start-to-end time range with pet(same/different) existing task | Prompts AI to suggest alternative times to reschedule new task with reasoning | Pass |
| "Add button" clicked for task with non-conflicting start-to-end time range| Prompts AI to analyze task details then suggest edits, and displays three buttons to actually add task to schedule, edit task details manually, or cancel the addition of the task entirely. | Pass |

## Sample Schedule Output
When "Sort by earliest datetime" is checked (no other filters applied) and user already marked the task as complete:
| Pet | Date | Time | Task | Duration(mins) | Frequency | Priority | Status |
|-----|------|------|------|----------------|-----------|----------|--------|
| Mochi | 2026-08-03 | 08:00 | Feeding | 10.0000 | Daily | high | pending |
| Bubble | 2026-08-03 | 10:30 | Morning feeding | 2.0000 | Daily | high | pending |
| Flora | 2026-08-03 | 20:00 | Feeding | 2.0000 | Daily | high | pending |
| Mochi | 2026-08-04 | 09:00 | Walk | 30.0000 | Daily | high | complete |

## 📸 Brief Demo Walkthrough

1. There is already an owner created, but if you want to create a new one, first fill in the owner name field then click the "Create Owner" button.
2. If you want to add a new pet to an existing owner, type in the owner name, pet name, and pet species, then click the "Add Pet" button.
3. To add a new task, select an owner and pet, enter a description and duration, select a frequency and priority, and enter the time to complete it by. If the new task is scheduled at the same time as an existing task, a warning will be displayed and the new task won't be added to the schedule.
4. To build a schedule, select an owner and perform one (or none if you want a general list) of the following actions: select a pet, select a completion_status, or check the "Sort by the earliest datetime" checkbox. 
5. To mark a task as complete, select an owner, a pet, and the task description corresponding to the task.

## Reflection
### How did you collaborate with AI?
I used AI to help design a system diagram for the AI feature I decided to integrate my application with: agentic workflow. I also found it helpful to consult when I was considering the most beneficial feedback the agent could provide after validating new tasks the user tried to enter. 

### Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
A simple issue (but didn't notice initially) I encountered when integrating the AI agent was successfully connecting the the Google Gemini API. I often faced an import error and the AI coding assistant made me realize that I actually hadn't downloaded `google-genai`. This prompted me to further add the module to `requirements.txt` so that I can ensure that my environment is successfully set up and that viewers are also aware of the needed library installments.

### Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
Once, the AI unnecessarily created a `pawpal_system.py` function that was very similar to `prepare_conflict_summary()`. All it did was reference key and value pairs in the result returned by `prepare_conflict_summary()` and basically return the same exact dictionary except for a couple additional values. Although I accepted these specific edits initially, I realized its redundancy after including print statements when manually testing the functions. Afterwards, I removed the function entirely because it complicates things and instead made `prepare_conflict_summary()` the primary source of the parameter for `get_recommendation_prompt()`.
