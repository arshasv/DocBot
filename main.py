import os
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from crewai.llm import LLM
from helpers.documentation_loader import helpers
import litellm
from helpers.crew import crew_job

litellm._turn_on_debug()


documentation_helper = helpers()
# Extract project details
extract_project_details = documentation_helper.extract_project_details
generate_final_document = documentation_helper.generate_final_document

# Extract inputs
overview_text, estimation_data = extract_project_details("inputs/overview.pdf", "inputs/estimation.xlsx")

# Run Crew
estimation_str = estimation_data.to_string(index=False)
crew = crew_job()
crew_object = crew.crew_run()
crew_object.kickoff(inputs={"overview": overview_text, "estimation": estimation_str})

# Output
generate_final_document(tasks=crew.create_tasks())
print("✅ Functional documentation generated.")
