from crewai.llm import LLM
from dotenv import load_dotenv
import os
from crewai import Crew, Agent, Task
from helpers.config_loader import ConfigLoader

load_dotenv()

class crew_job:
    def __init__(self):
        # Load agent & task YAMLs
        self.config_loader = ConfigLoader()
        self.agents_config = self.config_loader.load_agents()
        self.tasks_config = self.config_loader.load_tasks()

        # Create LLM instances
        self.gemini_llm = LLM(
            provider="gemini",
            model=os.getenv("MODEL"),
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.azure_gpt_llm = LLM(
            provider="openai",
            model=os.getenv("MODEL_NAME"),
            api_key=os.getenv("OPENAI_API_KEY"),
            api_base=os.getenv("OPENAI_API_BASE"),
        )

    def create_agents(self):
        self.agents = {}
        for name, config in self.agents_config.items():
            if config["llm"] == "gemini":
                llm_instance = self.gemini_llm
            elif config["llm"] == "azure-gpt-4":
                llm_instance = self.azure_gpt_llm
            else:
                raise ValueError(f"Unknown LLM: {config['llm']}")

            self.agents[name] = Agent(
                name=config["name"],
                role=config["role"],
                goal=config["goal"],
                backstory=config["backstory"],
                llm=llm_instance
            )
        return self.agents
        # Create Tasks
    def create_tasks(self):    
        self.tasks = []
        for task_cfg in self.tasks_config:
            agent_name = task_cfg.pop("agent") 
            print(agent_name)
            agents = self.create_agents()
            agent_obj = agents[agent_name]     
            self.tasks.append(Task(**task_cfg, agent=agent_obj))   
        return  self.tasks
    def crew_run(self):
        if not hasattr(self, "agents"):
            self.create_agents()
        if not hasattr(self, "tasks"):
            self.create_tasks()
        # Create Crew instance
        crew = Crew(agents=list(self.agents.values()), tasks=self.tasks)
        # Run the crew job
        return crew
