import subprocess
import json
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SteampipeError(Exception):
    """Custom exception for Steampipe-related errors"""
    pass

def run_steampipe(query: str, workspace_path: str) -> Dict[str, Any]:
    """
    Execute a Steampipe query in a specific workspace.
    
    Args:
        query (str): The SQL query to execute
        workspace_path (str): Path to the Steampipe workspace
        
    Returns:
        Dict[str, Any]: The query results as a dictionary
        
    Raises:
        SteampipeError: If there's an error executing the query
    """
    try:
        # Ensure workspace path exists
        if not os.path.exists(workspace_path):
            raise SteampipeError(f"Workspace path does not exist: {workspace_path}")

        # Construct the command
        cmd = f"steampipe query --output json --workspace {workspace_path} \"{query}\""
        
        # Execute the command
        logger.debug(f"Executing Steampipe command: {cmd}")
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
        
        # Parse the JSON output
        return json.loads(result)
        
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"Steampipe execution error: {error_message}")
        raise SteampipeError(f"Failed to execute Steampipe query: {error_message}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Steampipe output: {e}")
        raise SteampipeError(f"Failed to parse Steampipe output: {str(e)}")
        
    except Exception as e:
        logger.error(f"Unexpected error during Steampipe execution: {e}")
        raise SteampipeError(f"Unexpected error: {str(e)}")

def setup_workspace(consultoria_id: int, credentials: Dict[str, Any]) -> str:
    """
    Set up a new Steampipe workspace for a consultoria.
    
    Args:
        consultoria_id (int): The ID of the consultoria
        credentials (Dict[str, Any]): Cloud provider credentials
        
    Returns:
        str: Path to the created workspace
    """
    workspace_path = f"/tmp/steampipe/workspaces/{consultoria_id}"
    
    try:
        # Create workspace directory
        os.makedirs(workspace_path, exist_ok=True)
        
        # Create config file
        config = {
            "aws": credentials.get("aws", {}),
            "gcp": credentials.get("gcp", {}),
            "azure": credentials.get("azure", {})
        }
        
        with open(f"{workspace_path}/config.json", "w") as f:
            json.dump(config, f, indent=2)
            
        return workspace_path
        
    except Exception as e:
        logger.error(f"Failed to setup Steampipe workspace: {e}")
        raise SteampipeError(f"Failed to setup workspace: {str(e)}")
