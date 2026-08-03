from dotenv import load_dotenv
load_dotenv()
import pytest
import pawpal_system
from datetime import date, timedelta
from llm_client import GeminiClient


# ============================================================================
# RECURRENCE LOGIC TESTS
# ============================================================================

def test_daily_task_recurrence_advances_due_date():
    """Verify Daily tasks advance due_date by 1 day when marked complete."""
    today = date.today()
    task = pawpal_system.Task("Morning feeding", 10, "Daily", "high", "09:00", due_date=today)

    print(f"\n🐾 TEST: Daily Task Recurrence")
    print(f"   Initial due_date: {task.due_date}")

    task.mark_complete()

    assert task.due_date == today + timedelta(days=1)
    assert task.completion_status == "complete"
    print(f"   ✅ Advanced to: {task.due_date}")


def test_weekly_task_recurrence_advances_by_seven_days():
    """Verify Weekly tasks advance due_date by 7 days when marked complete."""
    today = date.today()
    task = pawpal_system.Task("Grooming", 60, "Weekly", "medium", "10:00", due_date=today)

    print(f"\n🐾 TEST: Weekly Task Recurrence")
    print(f"   Initial due_date: {task.due_date}")

    task.mark_complete()

    assert task.due_date == today + timedelta(weeks=1)
    assert task.completion_status == "complete"
    print(f"   ✅ Advanced to: {task.due_date} (7 days later)")


# ============================================================================
# CONFLICT DETECTION TEST
# ============================================================================

def test_conflict_detection_blocks_overlapping_tasks():
    """Verify TaskValidator detects when two tasks overlap on the same day."""
    today = date.today()
    dog = pawpal_system.Pet("Buddy", "Dog")
    scheduler = pawpal_system.Scheduler([dog])
    validator = pawpal_system.TaskValidator(scheduler)

    task1 = pawpal_system.Task("Morning walk", 30, "Daily", "high", "09:00", due_date=today)
    task2 = pawpal_system.Task("Vet checkup", 45, "Daily", "high", "09:15", due_date=today)

    print(f"\n🔄 TEST: Conflict Detection")
    print(f"   Task 1: {task1.description} 09:00 (30 mins)")
    print(f"   Task 2: {task2.description} 09:15 (45 mins)")

    scheduler.add_task(dog.name, task1)
    conflict_summary = validator.prepare_conflict_summary(dog.name, task2)

    assert conflict_summary["status"] == "conflict_detected"
    assert conflict_summary["conflicting_task"]["description"] == "Morning walk"
    print(f"   ✅ Conflict detected: Tasks overlap")


# ============================================================================
# SORTING TEST
# ============================================================================

def test_sort_by_time_orders_across_pets():
    """Verify sort_by_time orders tasks from multiple pets earliest to latest by datetime, regardless of which pet owns them."""
    today = date.today()
    dog = pawpal_system.Pet("Rex", "Dog")
    cat = pawpal_system.Pet("Momo", "Cat")
    scheduler = pawpal_system.Scheduler([dog, cat])
    scheduler.add_task(dog.name, pawpal_system.Task("Walk", 30, "Daily", "high", "14:00", due_date=today))
    scheduler.add_task(cat.name, pawpal_system.Task("Feed", 10, "Daily", "high", "08:00", due_date=today+timedelta(days=2)))
    scheduler.add_task(dog.name, pawpal_system.Task("Groom", 20, "Weekly", "low", "10:00", due_date=today))

    print(f"\n⏰ TEST: Sort By DateTime (Across Multiple Pets)")
    print(f"   Pets: {dog.name}, {cat.name}")
    print(f"   Date: {today}")
    print(f"   Tasks added (unordered):")
    for pet in [dog, cat]:
        for task in pet.tasks:
            print(f"     - {task.description} ({task.time}) - {pet.name}")

    scheduler = pawpal_system.Scheduler([dog, cat])
    ordered = scheduler.sort_by_time([dog, cat])

    print(f"   After sorting by datetime:")
    for i, task in enumerate(ordered):
        print(f"     {i+1}. {task.description} at {task.time} on {task.due_date}")

    # Assert the tasks are sorted by earliest to latest datetime (date first, then time)
    assert len(ordered) == 3, f"Expected 3 tasks, got {len(ordered)}"

    # Check each task in order
    assert ordered[0].description == "Groom" and ordered[0].due_date == today and ordered[0].time == "10:00"
    assert ordered[1].description == "Walk" and ordered[1].due_date == today and ordered[1].time == "14:00"
    assert ordered[2].description == "Feed" and ordered[2].due_date == today + timedelta(days=2) and ordered[2].time == "08:00"

    # Verify the datetimes are in ascending order
    datetimes = [(task.due_date, task.time) for task in ordered]
    assert datetimes == [(today, "10:00"), (today, "14:00"), (today + timedelta(days=2), "08:00")]

    print(f"   ✅ Test passed!\n")



# ============================================================================
# EDGE CASE TEST
# ============================================================================

def test_handle_empty_pet_task_list():
    """Verify filtering works gracefully when a pet has no tasks."""
    dog = pawpal_system.Pet("Buddy", "Dog")
    cat = pawpal_system.Pet("Whiskers", "Cat")
    scheduler = pawpal_system.Scheduler([dog, cat])

    scheduler.add_task(dog.name, pawpal_system.Task("Walk", 30, "Daily", "high", "09:00"))

    print(f"\n🐱 TEST: Filter Empty Pet Task List")
    print(f"   Dog tasks: {len(dog.tasks)}")
    print(f"   Cat tasks: {len(cat.tasks)}")

    filtered = scheduler.filter_tasks(pet_name="Whiskers")

    assert filtered == []
    assert len(dog.tasks) == 1
    assert len(cat.tasks) == 0
    print(f"   ✅ Gracefully handled empty task list")


# ============================================================================
# AI AGENT TEST
# ============================================================================

def test_gemini_client_with_validator_conflict_prompt():
    """Integration test: Generate conflict prompt with validator and analyze with Gemini API."""
    print(f"\n🤖 TEST: Gemini API Integration with Validator")

    today = date.today()
    dog = pawpal_system.Pet("Rex", "Golden Retriever")
    scheduler = pawpal_system.Scheduler([dog])
    validator = pawpal_system.TaskValidator(scheduler)

    task1 = pawpal_system.Task("Morning walk", 30, "Daily", "high", "07:00", due_date=today)
    task2 = pawpal_system.Task("Breakfast", 20, "Daily", "high", "07:15", due_date=today)

    scheduler.add_task(dog.name, task1)
    conflict_summary = validator.prepare_conflict_summary(dog.name, task2)

    print(f"   Conflict detected: {conflict_summary['status']}")

    prompt = validator.get_recommendation_prompt(conflict_summary)
    print(f"   Sending conflict resolution prompt to Gemini API...")

    client = GeminiClient()
    recommendation = client.get_client_analysis(prompt)

    assert len(recommendation) > 0
    print(f"   ✅ Gemini API returned: {recommendation[:100]}...")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
