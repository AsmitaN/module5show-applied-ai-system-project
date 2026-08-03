from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, TaskValidator
from llm_client import GeminiClient
from datetime import date

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Initialize session state
if "owners" not in st.session_state:
    st.session_state.owners = {}
    st.session_state.owners["Jordan"] = Owner("Jordan")
    new_pet = Pet("Mochi", "Golden Retriever")
    st.session_state.owners["Jordan"].add_pet(new_pet)

if "current_owner" not in st.session_state:
    st.session_state.current_owner = None

st.subheader("👤 Owner & Pet Setup")

owner_name = st.text_input("Owner name", placeholder="Enter owner name")
pet_name = st.text_input("Pet name", placeholder="Enter pet name")
species = st.text_input("Species", placeholder="Enter pet species (i.e. Golden Retriever)")

col1, col2 = st.columns(2)
with col1:
    if st.button("Create Owner"):
        if owner_name == "":
            st.error("Please enter an owner name")
            st.stop()
        elif owner_name in st.session_state.owners:
            st.warning(f"Owner '{owner_name}' already exists")
            st.session_state.current_owner = owner_name
        else:
            st.session_state.owners[owner_name] = Owner(owner_name)
            st.session_state.current_owner = owner_name
            st.success(f"Created owner: {owner_name}")

with col2:
    if st.button("Add Pet"):
        if owner_name == "":
            st.error("Please enter the owner's name of the pet to be added")
            st.stop()
        if pet_name == "" or species == "":
            st.error("Please enter all values needed to add a new pet")
            st.stop()
        current_owner = st.session_state.owners[owner_name]
        pet_exists = any(pet.name == pet_name for pet in current_owner.pets)
        if pet_exists:
            st.warning(f"Pet '{pet_name}' already exists for {current_owner.name}")
        else:
            new_pet = Pet(pet_name, species)
            current_owner.add_pet(new_pet)
            st.success(f"Added {pet_name} ({species})")

# Display created owners and their pets
if st.session_state.owners:
    st.write("**Created Owners:**")
    for owner_key, owner_obj in st.session_state.owners.items():
        st.write(f"\n**{owner_obj.name}**")
        if owner_obj.pets:
            for pet in owner_obj.pets:
                st.write(f"  - {pet.get_info()}")
        else:
            st.write("  *(no pets yet)*")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2 = st.columns(2)
with col1:
    owner_name = st.selectbox("Owner", options=list(st.session_state.owners.keys()), index=0, key="owner_name_tasks")
    current_owner = st.session_state.owners[owner_name]
with col2:
    current_owner = st.session_state.owners[owner_name]
    pet_name = st.selectbox("Pet", options=(pet.name for pet in current_owner.pets), index=0, key="owner_pet_name_tasks")

col1, col2, col3 = st.columns(3)
with col1:
    task_description = st.text_input("Description", placeholder="Enter a short title for the task")
with col2:
    duration = st.number_input("Duration (minutes)", placeholder="Enter how long the task will take")
with col3:
    due_date = st.date_input("Pick a date")

col1, col2, col3 = st.columns(3)
with col1:
    frequency = st.selectbox("Frequency", ["Daily", "Weekly"], index=0)
with col2:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=0)
with col3:
    time = st.text_input("Time to complete by", placeholder="Enter in HH:MM format")

current_owner.scheduler = Scheduler(current_owner.pets)
current_owner.task_validator = TaskValidator(current_owner.scheduler)

if st.button("Add task"):
    if task_description!="" and duration!="" and frequency!="" and priority!="" and time!="":
        client = GeminiClient()
        new_task = Task(task_description, duration, frequency, priority, time, due_date=due_date)
        #time_conflict_exists = current_owner.scheduler.check_scheduling_conflicts(pet_name, new_task)
        conflict_summary = current_owner.task_validator.prepare_conflict_summary(pet_name, new_task)
        #time_conflict_report = current_owner.task_validator.suggest_resolution(pet_name, new_task)
        if conflict_summary["status"] == "conflict_detected":
            prompt = current_owner.task_validator.get_recommendation_prompt(conflict_summary)
            recommendation = client.get_client_recommendation(prompt)
            st.info(recommendation)
        else:
            # No conflict: get task analysis
            analysis_prompt = current_owner.task_validator.get_task_analysis_prompt(pet_name, new_task)
            analysis = client.get_client_recommendation(analysis_prompt)  # Reuse same client
            
            st.session_state.task_pending_review = {
                "task": new_task,
                "pet_name": pet_name,
                "analysis": analysis
            }
            st.session_state.show_analysis = True
            #current_owner.scheduler.add_task(pet_name, new_task)
            #st.success(f"Added new task: {task_description} - {pet_name}")
        ##time_conflict_report = current_owner.schedule_optimizer.suggest_resolution(pet_name, new_task)
        ##if time_conflict_report["status"] == "no_conflict":
            # don't suggest anything new, display "The task was successfully added!"
            ##current_owner.scheduler.add_task(pet_name, new_task)
            ##st.success(f"Added new task: {task_description} - {pet_name}")
        # if time_conflict_exists == False:
        #     current_owner.scheduler.add_task(pet_name, new_task)
        #     st.success(f"Added new task: {task_description} - {pet_name}")
        ##else:
            ##st.write("TIME CONFLICT DETECTED")
            ##user_selected_alternative_time = st.radio(label="Choose an alternative time:", options=time_conflict_report["alternative_times"])
            #st.warning("⚠️ TIME CONFLICT DETECTED. See terminal for more details")

    else:
        st.error("Please enter all values needed to add a new task")
        st.stop()

if st.session_state.get("show_analysis"):
    pending = st.session_state.task_pending_review
    st.info("### AI Analysis\n" + pending["analysis"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Add Task"):
            current_owner.scheduler.add_task(pending["pet_name"], pending["task"])
            st.success(f"Added: {pending['task'].description}")
            st.session_state.show_analysis = False
            st.session_state.task_pending_review = None
    
    with col2:
        if st.button("✏️ Edit Task"):
            st.info("Modify the task details above and click 'Add task' again")
            st.session_state.show_analysis = False
            st.session_state.task_pending_review = None

# Debug: Display all created tasks
st.markdown("### 🐛 Debug: Created Tasks")
with st.expander("Show all tasks by pet", expanded=False):
    if current_owner.pets:
        for pet in current_owner.pets:
            st.write(f"**{pet.get_info()}**")
            if pet.tasks:
                for task in pet.tasks:
                    st.write(f"  - {task.get_info()}")
            else:
                st.write("  *(no tasks)*")
    else:
        st.info("No pets created yet.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

owner_name = st.selectbox("Owner", options=list(st.session_state.owners.keys()), index=0, key="owner_name_schedule")
current_owner = st.session_state.owners[owner_name]
if current_owner.scheduler:
    current_owner.scheduler.retrieve_all_tasks()
    current_owner.scheduler.reset_completed_tasks_to_pending(date.today())

col1, col2, col3 = st.columns(3)

with col1:
    pet_options = [""] + [pet.name for pet in current_owner.pets]
    pet_name = st.selectbox("Pet", options=pet_options, index=0, key="owner_pet_name_schedule")
with col2:
    completion_options = ["", "pending", "complete"]
    completion_status = st.selectbox("Completion Status", options=completion_options, index=0)
with col3:
    sort_by_time = st.checkbox("Sort by earliest datetime", value=False)

if st.button("Generate schedule"):
    schedule_to_display = None

    if pet_name:
        schedule_to_display = current_owner.scheduler.filter_tasks(pet_name=pet_name)
        st.subheader(f"Schedule for {pet_name}")
    elif completion_status:
        schedule_to_display = current_owner.scheduler.filter_tasks(completion_status=completion_status)
        st.subheader(f"Schedule ({completion_status} tasks)")
    elif sort_by_time:
        schedule_to_display = current_owner.scheduler.sort_by_time(current_owner.pets)
        st.subheader("Schedule (sorted by earliest datetime)")
    else:
        schedule_to_display = current_owner.scheduler.tasks
        st.subheader("Full Schedule")

    if schedule_to_display:
        # Convert tasks to table format with pet name
        task_data = []
        for task in schedule_to_display:
            # Find which pet this task belongs to
            pet_owner = ""
            for pet in current_owner.pets:
                if task in pet.tasks:
                    pet_owner = pet.name
                    break

            task_data.append({
                "Pet": pet_owner,
                "Date": str(task.due_date),
                "Time": task.time,
                "Task": task.description,
                "Duration (mins)": task.duration,
                "Frequency": task.frequency,
                "Priority": task.priority,
                "Status": task.completion_status
            })

        if task_data:
            st.table(task_data)
        else:
            st.info("No tasks found for this filter.")
    else:
        st.info("No tasks found for this filter.")

st.subheader("Completed a task?")
col1, col2, col3 = st.columns(3)

with col1:
    owner_name = st.selectbox("Owner", options=list(st.session_state.owners.keys()), index=0, key="owner_name_mark_complete")
    current_owner = st.session_state.owners[owner_name]
with col2:
    pet_name = st.selectbox("Pet", options=(pet.name for pet in current_owner.pets), index=0, key="owner_pet_name_mark_complete")
if current_owner.scheduler:
    with col3:
        selected_pet_tasks = [task for pet in current_owner.pets if pet.name == pet_name for task in pet.tasks]
        task_description = st.selectbox("Task description", options=(task.description for task in selected_pet_tasks), index=0, key="owner_task_name_mark_complete")

if st.button("Submit"):
    for pet in current_owner.pets:
        if pet_name == pet.name:
            for task in pet.tasks:
                if task_description == task.description:
                    task.mark_complete()
                    print("BEFORE RESET: Marked as complete?: " + str(task.completion_status == "complete"))
                    st.success(f"{task_description} marked as complete (and will be reset to pending after this message)")
                    current_owner.scheduler.reset_completed_tasks_to_pending(date.today())
                    print("AFTER RESET: Marked as complete?: " + str(task.completion_status == "complete"))