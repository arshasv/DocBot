import os
from dotenv import load_dotenv
from helper import extract_project_details, generate_final_document
from crewai import Crew, Agent, Task
from crewai.llm import LLM
import yaml
import litellm

litellm._turn_on_debug()

# Load .env variables
load_dotenv()

# Load agent & task YAMLs
with open("config/agents.yaml") as f:
    agents_config = yaml.safe_load(f)

with open("config/tasks.yaml") as f:
    tasks_config = yaml.safe_load(f)

# Create LLM instances
gemini_llm = LLM(
    provider="gemini",
    model=os.getenv("MODEL"),  # e.g., "gemini/gemini-pro"
    api_key=os.getenv("GEMINI_API_KEY")
)

azure_gpt_llm = LLM(
    provider="azure",
    model=os.getenv("MODEL_NAME"),  # e.g., "gpt-4"
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_API_BASE"),
    api_version=os.getenv("OPENAI_API_VERSION")
)

# Create Agents
agents = {}
for name, config in agents_config.items():
    if config["llm"] == "gemini":
        llm_instance = gemini_llm
    elif config["llm"] == "azure-gpt-4":
        llm_instance = azure_gpt_llm
    else:
        raise ValueError(f"Unknown LLM: {config['llm']}")

    agents[name] = Agent(
        name=config["name"],
        role=config["role"],
        goal=config["goal"],
        backstory=config["backstory"],
        llm=llm_instance
    )

# Create Tasks
tasks = []
for task_cfg in tasks_config:
    agent_name = task_cfg.pop("agent")  # Remove 'agent' from the dict
    agent_obj = agents[agent_name]      # Lookup the actual Agent object
    tasks.append(Task(**task_cfg, agent=agent_obj))

# Extract inputs
overview_text, estimation_data = extract_project_details("inputs/overview.pdf", "inputs/estimation.xlsx")

# Run Crew
estimation_str = estimation_data.to_string(index=False)

crew = Crew(agents=list(agents.values()), tasks=tasks)
crew.kickoff(inputs={"overview": overview_text, "estimation": estimation_str})

# Output
generate_final_document(tasks)
print("✅ Functional documentation generated.")
