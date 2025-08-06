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
class ConfigLoader:
    def __init__(self, agents_path="config/agents.yaml", tasks_path="config/tasks.yaml"):
        self.agents_path = agents_path
        self.tasks_path = tasks_path

    def load_agents(self):
        return self._load_yaml(self.agents_path)

    def load_tasks(self):
        return self._load_yaml(self.tasks_path)

    def _load_yaml(self, path):
        with open(path, 'r') as file:
            return yaml.safe_load(file)
        
config_loader = ConfigLoader()
agents_config = config_loader.load_agents()
tasks_config = config_loader.load_tasks()
# with open("config/agents.yaml") as f:
#     agents_config = yaml.safe_load(f)

# with open("config/tasks.yaml") as f:
#     tasks_config = yaml.safe_load(f)

# Create LLM instances
gemini_llm = LLM(
    provider="gemini",
    model=os.getenv("MODEL"), 
    api_key=os.getenv("GEMINI_API_KEY")
)

azure_gpt_llm = LLM(
    provider="openai",
    model=os.getenv("MODEL_NAME"), 
    api_key=os.getenv("OPENAI_API_KEY"),
    api_base=os.getenv("OPENAI_API_BASE"),
    # api_version=os.getenv("OPENAI_API_VERSION")

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
    agent_name = task_cfg.pop("agent") 
    agent_obj = agents[agent_name]     
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
