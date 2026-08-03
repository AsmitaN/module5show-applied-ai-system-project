# Applied AI System Project Reflection

## Limitations, Biases, and Reliability
One limitation about my AI is that it doesn't provide a detailed summary of what can be improved for a non-conflicting task. I went instead for a concise summary because the application assumes that the user comes with a decent background in pet care. In other words, it assumes that the owner is not a beginner pet owner, so the feedback it returns for a valid task may not be detailed enough.\
A potential bias for my AI would have been only including the start time in the prompt (which I don't), but I include the approximate end time for each task to narrow down conflicting time ranges the new task could fall in. If I didn't include time ranges, the response would result in alternative start times for conflicting tasks because the duration of the task isn't actually considered.\
I don't think my AI could be misused because API calls are only made during a specific state change ("Add task" button and task fields are non-empty), and with two scenario-specific prompts generated with TaskValidator's help.\
Something that surprised me while testing my AI's reliability is that the review for a non-conflicting task was very balanced. It makes note of the pet's breed and gives the user a brief overview of changes they could make that would better address their pet's health. I also like the way it provides reasoning for its top three choices of alternative times, using accessible data to support the recommendations.

### How did you collaborate with AI?
I used AI to help design a system diagram for the AI feature I decided to integrate my application with: agentic workflow. I also found it helpful to consult when I was considering the most beneficial feedback the agent could provide after validating new tasks the user tried to enter. 

## Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
A simple issue (but didn't notice initially) I encountered when integrating the AI agent was successfully connecting the the Google Gemini API. I often faced an import error and the AI coding assistant made me realize that I actually hadn't downloaded `google-genai`. This prompted me to further add the module to `requirements.txt` so that I can ensure that my environment is successfully set up and that viewers are also aware of the needed library installments.

## Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
Once, the AI unnecessarily created a `pawpal_system.py` function that was very similar to `prepare_conflict_summary()`. All it did was reference key and value pairs in the result returned by `prepare_conflict_summary()` and basically return the same exact dictionary except for a couple additional values. Although I accepted these specific edits initially, I realized its redundancy after including print statements when manually testing the functions. Afterwards, I removed the function entirely because it complicates things and instead made `prepare_conflict_summary()` the primary source of the parameter for `get_recommendation_prompt()`.

