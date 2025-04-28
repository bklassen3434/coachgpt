from python_agent import SoftballAnalysisAgent
from langchain_openai import ChatOpenAI
import os
from pathlib import Path
from typing import Tuple, List, Optional

class PromptRouter:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4o-mini",  # fast and cheap
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.viz_dir = Path('visualizations')
        self.viz_dir.mkdir(exist_ok=True)

        # ✅ Initialize the SoftballAnalysisAgent once here
        self.analysis_agent = SoftballAnalysisAgent(
            db_path="structured/sqllite_db.db",
            table_name="yakkertech"
        )

    def _check_relevance(self, user_prompt: str) -> bool:
        """Determine if the prompt is relevant (softball-related)."""
        relevance_prompt = f"""
        You are an assistant checking whether a user's prompt is RELEVANT to softball, 
        softball statistics, softball visualizations, or databases about softball.
        
        If the prompt is clearly about softball-related analytics, statistics, rules, databases, players, games, or visualizations, respond with "yes".
        
        Otherwise, respond with "no".

        Prompt: {user_prompt}
        """

        response = self.llm.invoke(relevance_prompt)
        relevance = response.content.strip().lower()

        if relevance not in ["yes", "no"]:
            print("Warning: Unexpected relevance response, defaulting to 'no'.")
            relevance = "no"

        return relevance == "yes"

    def _classify_prompt(self, user_prompt: str) -> str:
        """Classify whether prompt is analysis or visualization related."""
        classification_prompt = f"""
        Classify the following prompt as either "analysis" or "visualization".
        Respond with only one word: either "analysis" or "visualization".

        Prompt: {user_prompt}
        """

        response = self.llm.invoke(classification_prompt)
        classification = response.content.strip().lower()

        if classification not in ["analysis", "visualization"]:
            print("Warning: Unexpected classification, defaulting to analysis.")
            classification = "analysis"

        return classification
    
    def _build_system_prompt(self, user_prompt: str, prompt_type: str) -> str:
        """Build the full system prompt based on prompt type"""
        
        # Get column descriptions first
        column_descriptions = self.analysis_agent._get_column_descriptions(user_prompt)
        
        if prompt_type == "analysis":
            return f"""You are a helpful assistant that can analyze softball data using Python.
            You have access to a dataframe called 'df' loaded from the 'yakkertech' table.

            Here are relevant column descriptions to help you understand the data:
            {column_descriptions}

            Use these descriptions to choose the correct columns when analyzing the data.
            Answer clearly and concisely."""
        
        elif prompt_type == "visualization":
            return f"""You are a helpful assistant that can create data visualizations using Python (matplotlib or seaborn).
            You have access to a dataframe called 'df' loaded from the 'yakkertech' table.

            Here are relevant column descriptions to help you understand the data:
            {column_descriptions}

            When creating a plot, always save the figure using plt.savefig('visualizations/plot.png').
            """

        else:
            raise ValueError("Invalid prompt type.")

    def _get_new_visualization(self, existing_images: set) -> Optional[str]:
        """Find newly created visualization if any."""
        current_images = set(self.viz_dir.glob('*.png'))
        new_images = current_images - existing_images
        
        if new_images:
            return str(max(new_images, key=lambda p: p.stat().st_ctime))
        return None

    def route(self, user_prompt: str, chat_history: List) -> Tuple[str, List, Optional[str]]:
        """Route user prompt to appropriate agent and handle visualization."""

        # Check if prompt is relevant
        is_relevant = self._check_relevance(user_prompt)
        if not is_relevant:
            return "Sorry, I can only help with softball-related questions.", chat_history, None
        
        # Classify prompt type
        prompt_type = self._classify_prompt(user_prompt)
        print(f"Routing to: {prompt_type.upper()} agent ✈️")

        # Build system prompt
        system_prompt = self._build_system_prompt(user_prompt, prompt_type)

        # Track existing visualizations
        existing_images = set(self.viz_dir.glob('*.png'))

        # Get response from agent
        answer, updated_chat_history = self.analysis_agent.process_prompt(
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            chat_history=chat_history
        )

        # Check for new visualization
        optional_plot = self._get_new_visualization(existing_images)

        return answer, updated_chat_history, optional_plot

# # Initialize global router
# router = PromptRouter()

# def route_user_prompt(user_prompt: str, chat_history: list) -> Tuple[str, List, Optional[str]]:
#     """Public routing interface."""
#     return router.route(user_prompt, chat_history)
