import sqlite3
import pandas as pd
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
import os
from query_vector_db import VectorDBQuerier
from tools import SmartPythonREPLTool

# ------------------ Overview ------------------ #
# This script defines a SoftballAnalysisAgent class that uses an LLM to analyze softball data.
# It provides functionality to load data from a SQLite database, query vector database for column descriptions,
# and create analysis or visualization prompts based on user input.

# Load environment variables
load_dotenv()

class SoftballAnalysisAgent:
    def __init__(self, 
                 db_path: str = "structured/sqllite_db.db", 
                 table_name: str = "yakkertech",
                 vector_db_path: str = "unstructured/vectordb",
                 collection_name: str = "data_dictionary"):
        self.db_path = db_path
        self.table_name = table_name
        self.collection_name = collection_name
        self.vector_db = VectorDBQuerier(db_path=vector_db_path)
        self.df = self._load_data()
        
    def _load_data(self) -> pd.DataFrame:
        """Connect to SQLite and load data into DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query(f"SELECT * FROM {self.table_name}", conn)

    def _get_column_descriptions(self, user_prompt: str) -> str:
        """Query vector DB for relevant column descriptions"""
        results = self.vector_db.query(user_prompt, self.collection_name, top_n=5)
        return "\n".join([column['document'] for column in results])

    def _setup_agent(self, system_message: str) -> AgentExecutor:
        """Set up the LLM agent with tools and prompt template"""
        llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        smart_tool = SmartPythonREPLTool(df=self.df)
        tools = [smart_tool]

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_tools_agent(llm, tools, prompt_template)
        return AgentExecutor(agent=agent, tools=tools, verbose=False)

    def process_prompt(self, user_prompt: str, system_message: str, chat_history: list) -> tuple[str, list]:
        """Process user prompt and return response with updated chat history"""
        
        # Setup and run agent
        agent_executor = self._setup_agent(system_message)
        response = agent_executor.invoke({
            "input": user_prompt,
            "chat_history": chat_history
        })

        # Update chat history
        chat_history.append({"role": "user", "content": user_prompt})
        chat_history.append({"role": "assistant", "content": response["output"]})
        
        return response["output"], chat_history

# def python_agent(user_prompt: str, system_prompt: str, chat_history: list, 
#                 db_path: str = "structured/sqllite_db.db", table_name: str = "yakkertech") -> tuple[str, list]:
#     """Main function that coordinates the agent's response to user prompts"""
#     agent = SoftballAnalysisAgent(db_path, table_name)
#     return agent.process_prompt(user_prompt, system_prompt, chat_history)
