"""
Python Runner tool — executes Python code in a subprocess and returns stdout/stderr.
"""

import logging
import os
import subprocess
import sys
import tempfile

from app.tools import register

logger = logging.getLogger(__name__)


@register
def run_python_code(code: str) -> str:
    """
    Execute a Python script and return the standard output or error.
    Use this for data analysis, complex algorithms, or verifying logic.
    The code runs in a separate process for basic isolation.

    :param code: The full Python code snippet to execute.
    """
    logger.info("Executing Python code via tool...")
    
    # Create a temporary file to hold the code
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    try:
        # Execute the code and capture output
        # Use the current python executable to ensure environment consistency
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30  # Prevent infinite loops
        )
        
        output = result.stdout
        error = result.stderr
        
        response = ""
        if output:
            response += f"--- STDOUT ---\n{output}\n"
        if error:
            response += f"--- STDERR ---\n{error}\n"
        
        if not response:
            return "Code executed successfully with no output."
        
        return response

    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (exceeded 30 seconds)."
    except Exception as e:
        logger.error(f"Code runner error: {e}")
        return f"Error during execution: {str(e)}"
    finally:
        # Cleanup the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
