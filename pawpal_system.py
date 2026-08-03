from typing import List
from datetime import date, timedelta

# Owner: Manages multiple pets and provides access to all their tasks.
class Owner:
    def __init__(self, name: str):
        self.name: str = name
        self.pets: List[Pet] = []
        self.scheduler: Scheduler = None
        self.task_validator: TaskValidator = None
    
    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

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
        """Mark the task as complete and advance due_date if recurring."""
        interval = self.FREQUENCY_INTERVALS.get(self.frequency)
        if interval:
            self.due_date += interval
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
    
    def retrieve_all_tasks(self):
        """Retrieve and aggregate all tasks from all pets."""
        self.tasks.clear()
        for pet in self.pets:
            self.tasks.extend(pet.tasks)

    def add_task(self, pet_name: str, task: 'Task') -> bool:
        """Add a task to a pet after checking for scheduling conflicts. Returns True if added, False if conflict blocked it."""
        pet = self.get_pet_by_name(pet_name)
        pet.tasks.append(task)
        # updates the scheduler's common list of tasks after every new task is added to a pet
        self.retrieve_all_tasks()
        return True

    def reset_completed_tasks_to_pending(self, reference_date: date = None) -> None:
        """Reset tasks with completion_status 'complete' back to 'pending' if their due_date matches reference_date."""
        for task in self.tasks:
            if task.completion_status == "complete" and task.due_date == reference_date:
                task.completion_status = "pending"

# Finds scheduling conflicts and generates prompts to receive alternative times or feedback on non-conflicting tasks.
class TaskValidator:
    
    def __init__(self, scheduler: Scheduler):
        self.scheduler: Scheduler = scheduler
        self.tasks: List[Task] = []

    def times_overlap(self, start1_str: str, duration1: int, start2_str: str, duration2: int) -> bool:
        """Check if two tasks overlap based on start time and duration."""
        h1, m1 = map(int, start1_str.split(':'))
        h2, m2 = map(int, start2_str.split(':'))

        start1_mins = h1 * 60 + m1
        start2_mins = h2 * 60 + m2
        end1_mins = start1_mins + duration1
        end2_mins = start2_mins + duration2

        # returns True if the tasks overlap at some point in time
        return start1_mins < end2_mins and start2_mins < end1_mins

    def find_occupied_times(self, due_date: date) -> List[str]:
        """Return a list of occupied time slots (HH:MM to HH:MM format) accounting for task duration on a given date."""
        occupied = []
        for pet in self.scheduler.pets:
            for task in pet.tasks:
                if task.due_date == due_date:
                    # parse start time
                    start_h, start_m = map(int, task.time.split(':'))
                    start_mins = start_h * 60 + start_m

                    # calculate end time based on duration
                    end_mins = start_mins + task.duration
                    end_h = end_mins // 60
                    end_m = end_mins % 60

                    # format as "HH:MM to HH:MM"
                    time_slot = f"{start_h:02d}:{start_m:02d} to {int(end_h):02d}:{int(end_m):02d}"
                    occupied.append(time_slot)
        return occupied

    def prepare_conflict_summary(self, pet_name: str, task: Task) -> dict:
        """Prepare structured conflict summary data for AI recommendation."""
        conflict_task = None
        conflicting_pet = None

        for pet in self.scheduler.pets:
            for existing_task in pet.tasks:
                if existing_task.due_date == task.due_date:
                    # if the the new task start/end times overlap with that of an 
                    # existing task
                    if self.times_overlap(task.time, task.duration, existing_task.time, existing_task.duration):
                        # saves the task and pet to explain reason for conflict
                        conflict_task = existing_task
                        conflicting_pet = pet
                        # exits from iterating through current pet's tasks
                        break
            # exits from iterating through other pets' task lists as conflict was 
            # already found
            if conflict_task:
                break
        # if the new task's start/end time doesn't concide with any of the pets' task lists
        if not conflict_task:
            return {"status": "no_conflict"}
        
        pet = self.scheduler.get_pet_by_name(pet_name)
        pet_info = f"{pet_name} ({pet.species})" if pet else pet_name

        # list of all time slots occupied by current tasks on a given day
        occupied_time_slots = self.find_occupied_times(task.due_date)

        conflict_summary = {
            "status": "conflict_detected",
            "new_task": {
                "description": task.description,
                "requested_time": task.time,
                "duration": task.duration,
                "due_date": str(task.due_date),
                "priority": task.priority,
                "frequency": task.frequency,
                "pet": pet_info
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

        return conflict_summary

    def get_recommendation_prompt(self, analysis_context: dict) -> str:
        """Generate a structured prompt for AI agent to recommend conflict resolution."""
        prompt = f"""
You are a pet care scheduling assistant. Analyze this scheduling conflict and recommend the best resolution.

Pet: {analysis_context["new_task"]["pet"]}

NEW TASK TO ADD:
- Description: {analysis_context["new_task"]["description"]}
- Requested Time: {analysis_context["new_task"]["requested_time"]}
- Duration: {analysis_context["new_task"]["duration"]} minutes
- Priority: {analysis_context["new_task"]["priority"]}
- Frequency: {analysis_context["new_task"]["frequency"]}

CONFLICTING WITH EXISTING TASK:
- Description: {analysis_context["conflicting_task"]["description"]}
- Date: {analysis_context["conflicting_task"]["due_date"]}
- Time: {analysis_context["conflicting_task"]["time"]}
- Duration: {analysis_context["conflicting_task"]["duration"]} minutes
- Pet: {analysis_context["conflicting_task"]["pet"]}

TIME SLOTS OCCUPIED BY CURRENT TASKS FROM ALL PETS:
{analysis_context["occupied_times"]}

Consider:
1. Pet health/safety (e.g., exercise needs, grooming frequency for the species)
2. Task priority and frequency
3. Reasonableness of each time slot
4. Pet routine and recovery time between activities

Recommend top three alternative times and explain why."""

        return prompt

    def get_task_analysis_prompt(self, pet_name: str, task: Task) -> str:
        """Generate a prompt for AI to analyze task details."""
        pet = self.scheduler.get_pet_by_name(pet_name)
        pet_info = f"{pet_name} ({pet.species})" if pet else pet_name
        
        prompt = f"""
    You are a pet care consultant. Analyze this task and provide brief, constructive feedback.

    PET: {pet_info}

    TASK TO ANALYZE:
    - Description: {task.description}
    - Duration: {task.duration} minutes
    - Time: {task.time}
    - Priority: {task.priority}
    - Frequency: {task.frequency}

    Consider:
    1. Is this activity appropriate for a {pet.species}?
    2. Is the duration reasonable?
    3. Does the frequency align with typical pet care needs?
    4. Any suggestions for improvement?

    Keep feedback concise (max 4-5 sentences) and supportive."""
        return prompt