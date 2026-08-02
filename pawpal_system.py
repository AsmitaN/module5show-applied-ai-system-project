from typing import List
from datetime import date, timedelta

# Stores pet details and a list of tasks.
class Pet:
    def __init__(self, name: str, species: str):
        self.name: str = name
        self.species: str = species
        self.tasks: List[Task] = []
    
    def get_name(self) -> str:
        """Return a string with the pet's name."""
        return f"{self.name}"

    def get_info(self) -> str:
        """Return a formatted string with the pet's name and species."""
        return f"{self.name} ({self.species})"

# Represents a single activity (description, time, frequency, priority, completion status).
class Task:
    FREQUENCY_INTERVALS = {
        "Daily": timedelta(days=1),
        "Weekly": timedelta(weeks=1),
    }

    def __init__(self, description: str, duration: int, frequency: str, priority: str, time: str, completion_status: str = "pending", due_date: date = date.today()):
        self.description = description
        self.duration = duration
        self.frequency = frequency
        self.priority = priority
        self.time = time
        self.due_date = due_date
        self.completion_status = completion_status
    
    def get_priority_level(self) -> int:
        """Return the numeric priority level (1=low, 2=medium, 3=high)."""
        priority_map = {"low": 1, "medium": 2, "high": 3}
        # converts priority to numerical version so that it is easier to compare against other tasks
        return priority_map.get(self.priority, 0)

    def get_info(self) -> str:
        """Return a formatted string with the task's details."""
        return f"{self.due_date} {self.time} - {self.description} ({self.duration} mins) [{self.priority}], {self.completion_status}"

    def mark_complete(self):
        """Mark the task as complete and advance due_date if recurring. Auto-resets recurring tasks to pending."""
        interval = self.FREQUENCY_INTERVALS.get(self.frequency)
        if interval:
            self.due_date += interval
            self.completion_status = "pending"
        else:
            self.completion_status = "complete"

# The "Brain" that retrieves, organizes, and manages tasks across pets.
class Scheduler:
    def __init__(self, pets: List['Pet']):
        self.pets = pets
        self.tasks: List[Task] = []

    def print_schedule(self, pets: List[Pet], schedule: List['Task']=None, pet_name: str = None):
        for pet in pets:
            print(pet.get_info())
            schedule_to_print = []
            # executes if a sorted/filtered schedule is passed
            if schedule:
                schedule_to_print = schedule
            # executes if no second argument was passed technically
            else:
                schedule_to_print = self.tasks
            for task in schedule_to_print:
                if task in pet.tasks:
                    print(task.get_info())
            if pet_name:
                break

    def sort_by_time(self, pets: List[Pet]) -> List[Task]:
        """Sort tasks from given pets by earliest to latest datetime (date first, then time)."""
        tasks = []
        for pet in pets:
            tasks.extend(pet.tasks)
        # Sort by due_date first, then by time (HH:MM format)
        return sorted(tasks, key=lambda task: (task.due_date, tuple(map(int, task.time.split(':')))))

    def get_pet_by_name(self, pet_name: str) -> Pet:
        """Return a Pet object with the corresponding pet_name."""
        return next((p for p in self.pets if p.name == pet_name), None)

    def filter_tasks(self, completion_status: str = None, pet_name: str = None) -> List[Task]:
        """Filter tasks by completion status or pet name."""
        filtered = self.tasks

        if completion_status:
            filtered = [task for task in filtered if task.completion_status == completion_status]

        if pet_name:
            pet = self.get_pet_by_name(pet_name)
            if pet:
                filtered = [task for task in filtered if task in pet.tasks]

        return filtered

    def check_scheduling_conflicts(self, pet_name: str, task: 'Task') -> bool:
        """Check if a task conflicts with existing tasks. Returns True if conflict exists, False if no conflict."""
        for pet in self.pets:
            for existing_task in pet.tasks:
                # checks if the time and date of an existing task coincides with the new task (same/different pets included)
                if existing_task.due_date == task.due_date and existing_task.time == task.time:
                    print(f"⚠️  CONFLICT DETECTED: Task '{task.description}' conflicts with existing task!")
                    print(f"   Existing: {existing_task.description} at {existing_task.time} on {existing_task.due_date} for {pet.name}")
                    print(f"   New task: {task.description} at {task.time} on {task.due_date} for {pet_name}")
                    # signals that scheduling conflict exists
                    return True
        # signals that there is no scheduling conflict after looping through each pet
        return False
    
    def retrieve_all_tasks(self):
        """Retrieve and aggregate all tasks from all pets."""
        self.tasks.clear()
        for pet in self.pets:
            self.tasks.extend(pet.tasks)

    def add_task(self, pet_name: str, task: 'Task') -> bool:
        """Add a task to a pet after checking for scheduling conflicts. Returns True if added, False if conflict blocked it."""
        pet = self.get_pet_by_name(pet_name)

        if self.check_scheduling_conflicts(pet_name, task):
            print(f"❌ Task not added due to scheduling conflict.")
            return False

        pet.tasks.append(task)
        # updates the scheduler's common list of tasks after every new task is added to a pet
        self.retrieve_all_tasks()
        return True

    def reset_completed_tasks_to_pending(self) -> None:
        """Reset all tasks with completion_status 'complete' back to 'pending'."""
        for task in self.tasks:
            if task.completion_status == "complete":
                task.completion_status = "pending"

class ScheduleOptimizer:
    """Intelligently resolves scheduling conflicts and optimizes task ordering."""

    def __init__(self, scheduler: Scheduler):
        self.scheduler: Scheduler = scheduler
        self.tasks: List[Task] = []
        self.optimized_order: List[Task] = []

    def times_overlap(self, start1_str: str, duration1: int, start2_str: str, duration2: int) -> bool:
        """Check if two tasks overlap based on start time and duration."""
        h1, m1 = map(int, start1_str.split(':'))
        h2, m2 = map(int, start2_str.split(':'))

        start1_mins = h1 * 60 + m1
        start2_mins = h2 * 60 + m2
        end1_mins = start1_mins + duration1
        end2_mins = start2_mins + duration2

        return start1_mins < end2_mins and start2_mins < end1_mins

    def find_occupied_times(self, due_date: date) -> List[str]:
        """Return a list of occupied time slots (HH:MM to HH:MM format) accounting for task duration on a given date."""
        occupied = []
        for pet in self.scheduler.pets:
            for task in pet.tasks:
                if task.due_date == due_date:
                    # Parse start time
                    start_h, start_m = map(int, task.time.split(':'))
                    start_mins = start_h * 60 + start_m

                    # Calculate end time based on duration
                    end_mins = start_mins + task.duration
                    end_h = end_mins // 60
                    end_m = end_mins % 60

                    # Format as "HH:MM to HH:MM"
                    time_slot = f"{start_h:02d}:{start_m:02d} to {int(end_h):02d}:{int(end_m):02d}"
                    occupied.append(time_slot)
        return occupied

    def suggest_resolution(self, pet_name: str, task: Task) -> dict:
        """Suggest alternative times when a scheduling conflict is detected."""
        conflict_task = None
        conflicting_pet = None

        for pet in self.scheduler.pets:
            for existing_task in pet.tasks:
                if existing_task.due_date == task.due_date:
                    if self.times_overlap(task.time, task.duration, existing_task.time, existing_task.duration):
                        conflict_task = existing_task
                        conflicting_pet = pet
                        break
            if conflict_task:
                break

        if not conflict_task:
            return {"status": "no_conflict"}

        #alternatives = self.generate_alternative_times(task)
        occupied_time_slots = self.find_occupied_times(task.due_date)

        suggestion = {
            "status": "conflict_detected",
            "new_task": {
                "description": task.description,
                "requested_time": task.time,
                "duration": task.duration,
                "due_date": str(task.due_date),
                "pet": pet_name
            },
            "conflicting_task": {
                "description": conflict_task.description,
                "time": conflict_task.time,
                "duration": conflict_task.duration,
                "due_date": str(conflict_task.due_date),
                "pet": conflicting_pet.name if conflicting_pet else "Unknown"
            },
            "occupied_times": occupied_time_slots
        }

        return suggestion

    def optimize_schedule(self) -> List[Task]:
        """Generate an optimized task order based on priority, due date, and time."""
        self.tasks = self.scheduler.tasks.copy()
        pending_tasks = [t for t in self.tasks if t.completion_status == "pending"]
        completed_tasks = [t for t in self.tasks if t.completion_status == "complete"]

        self.optimized_order = sorted(
            pending_tasks,
            key=lambda t: (-t.get_priority_level(), t.due_date, tuple(map(int, t.time.split(':'))))
        )
        self.optimized_order.extend(completed_tasks)

        return self.optimized_order

    def explain_ordering(self) -> str:
        """Return a human-readable explanation of the optimized task ordering."""
        if not self.optimized_order:
            return "No tasks to optimize."

        explanation = "Schedule Optimization Report:\n"
        explanation += "=" * 50 + "\n"
        explanation += "Tasks are ordered by:\n"
        explanation += "1. Priority (High → Medium → Low)\n"
        explanation += "2. Due date (earliest first)\n"
        explanation += "3. Time of day (earliest first)\n\n"
        explanation += "Optimized Order:\n"
        explanation += "-" * 50 + "\n"

        for i, task in enumerate(self.optimized_order, 1):
            priority_label = "HIGH" if task.get_priority_level() == 3 else ("MEDIUM" if task.get_priority_level() == 2 else "LOW")
            status = "✓" if task.completion_status == "complete" else "○"
            explanation += f"{i}. {status} [{priority_label}] {task.description}\n"
            explanation += f"   Due: {task.due_date} at {task.time} ({task.duration} mins)\n"

        return explanation

    def prepare_conflict_analysis(self, pet_name: str, task: Task, conflict_report: dict) -> dict:
        """Prepare structured conflict analysis data for AI recommendation."""
        if conflict_report["status"] == "no_conflict":
            return {"status": "no_conflict"}

        pet = self.scheduler.get_pet_by_name(pet_name)
        pet_info = f"{pet.name} ({pet.species})" if pet else pet_name

        analysis_context = {
            "pet": pet_info,
            "new_task": {
                "description": conflict_report["new_task"]["description"],
                "requested_time": conflict_report["new_task"]["requested_time"],
                "duration": conflict_report["new_task"]["duration"],
                "priority": task.priority,
                "frequency": task.frequency,
                "due_date": task.due_date
            },
            "conflicting_task": {
                "description": conflict_report["conflicting_task"]["description"],
                "time": conflict_report["conflicting_task"]["time"],
                "duration": conflict_report["conflicting_task"]["duration"],
                "pet": conflict_report["conflicting_task"]["pet"],
                "due_date": conflict_report["conflicting_task"]["due_date"]
            },
            "occupied_times": conflict_report["occupied_times"]
        }

        return analysis_context

    def get_recommendation_prompt(self, analysis_context: dict) -> str:
        """Generate a structured prompt for AI agent to recommend conflict resolution."""
        #if analysis_context.get("status") == "no_conflict":
            #return ""

        prompt = f"""You are a pet care scheduling assistant. Analyze this scheduling conflict and recommend the best resolution.

Pet: {analysis_context['pet']}

NEW TASK TO ADD:
- Description: {analysis_context['new_task']['description']}
- Requested Time: {analysis_context['new_task']['requested_time']}
- Duration: {analysis_context['new_task']['duration']} minutes
- Priority: {analysis_context['new_task']['priority']}
- Frequency: {analysis_context['new_task']['frequency']}

CONFLICTING WITH EXISTING TASK:
- Description: {analysis_context['conflicting_task']['description']}
- Date: {analysis_context['conflicting_task']['due_date']}
- Time: {analysis_context['conflicting_task']['time']}
- Duration: {analysis_context['conflicting_task']['duration']} minutes
- Pet: {analysis_context['conflicting_task']['pet']}

TIME SLOTS OCCUPIED BY CURRENT TASKS:
{analysis_context["occupied_times"]}

Consider:
1. Pet health/safety (e.g., exercise needs, grooming frequency for the species)
2. Task priority and frequency
3. Reasonableness of each time slot
4. Pet routine and recovery time between activities

Recommend top three alternative times is best and explain why. If no alternatives, suggest next steps."""

        return prompt

    def get_ai_recommendation(self, analysis_context: dict, api_key: str) -> str:
        """Get AI recommendation using Gemini API."""
        genai.configure(api_key=api_key)
        
        prompt = self.get_recommendation_prompt(analysis_context)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return response.text

# Owner: Manages multiple pets and provides access to all their tasks.
class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = None
        self.schedule_optimizer: ScheduleOptimizer = None
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)