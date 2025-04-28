import io
import contextlib
import pandas as pd
from langchain_experimental.tools import PythonREPLTool

class SmartPythonREPLTool(PythonREPLTool):
    def __init__(self, df: pd.DataFrame):
        """
        A Python tool that executes agent-written code, with access to the provided DataFrame 'df'.
        """
        super().__init__()
        self._local_vars = {"df": df}

    def run(self, command: str, **kwargs) -> str:
        """
        Execute Python code and return both printed output and evaluated results.
        
        Args:
            command (str): Python code to execute
            **kwargs: Additional keyword arguments
            
        Returns:
            str: Combined output of printed statements and evaluated results
        """
        try:
            # Handle case where input is a dict with 'query' key instead of raw string
            if isinstance(command, dict) and "query" in command:
                command = command["query"]

            # Set up string buffer to capture printed output
            buffer = io.StringIO()
            
            # Prepare execution environment with access to global namespace
            exec_globals = globals()
            # Add local variables (like DataFrame) to execution environment
            exec_globals.update(self._local_vars)
            # Empty dict for local variables created during execution
            exec_locals = {}

            # Split code into body statements and final expression
            # Body can have multiple lines, last line is treated as expression to evaluate
            lines = command.strip().split("\n")
            *body, last = lines if len(lines) > 1 else ("", lines[0])

            # Join body lines back together
            body_code = "\n".join(body)

            # Redirect stdout to capture printed output
            with contextlib.redirect_stdout(buffer):
                # Execute body code if it exists
                if body_code.strip():
                    exec(body_code, exec_globals, exec_locals)
                # Evaluate final expression
                result = eval(last, exec_globals, exec_locals)

            # Get any printed output from the buffer
            printed_output = buffer.getvalue().strip()

            # Combine printed output and evaluation result
            final_output = ""
            if printed_output:  # Add any printed statements
                final_output += printed_output
            if result is not None:  # Add evaluated result if not None
                final_output += "\n" + str(result)


            return final_output.strip()

        except Exception as e:
            # Return error message if code execution fails
            return f"Error executing Python code: {e}"
