#!/usr/bin/env python3
import os
import sys
import importlib.util
import inspect
import logging
from typing import List, Type

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

logger.info("=" * 50)
logger.info("Starting MCP server script...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Script location: {__file__}")
logger.info(f"Environment PORT: {os.environ.get('PORT')}")
logger.info(f"Environment MCP_PORT: {os.environ.get('MCP_PORT')}")
logger.info(f"Python path: {sys.path}")
logger.info("=" * 50)

# Try importing required modules with detailed error handling
try:
    import uvicorn
    logger.info("✓ uvicorn imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import uvicorn: {e}")
    sys.exit(1)

try:
    import argparse
    logger.info("✓ argparse imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import argparse: {e}")
    sys.exit(1)

try:
    from agency_swarm.tools import BaseTool
    logger.info("✓ agency_swarm.tools.BaseTool imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import agency_swarm.tools.BaseTool: {e}")
    logger.error("Make sure agency-swarm is installed: pip install agency-swarm>=1.0.0b5")
    sys.exit(1)

try:
    from agency_swarm.integrations.mcp_server import run_mcp
    logger.info("✓ agency_swarm.integrations.mcp_server.run_mcp imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import agency_swarm.integrations.mcp_server.run_mcp: {e}")
    sys.exit(1)

logger.info("All imports successful!")

# Default configuration
DEFAULT_TOOLS_DIR = "./tools"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_INSTANCE_NAME = "mcp-server"

def get_config():
    """Get configuration from environment variables with CLI argument overrides"""
    # Read from environment variables first
    tools_dir = os.getenv("MCP_TOOLS_DIR", DEFAULT_TOOLS_DIR)
    host = os.getenv("MCP_HOST", DEFAULT_HOST)
    port = int(os.getenv("MCP_PORT", str(DEFAULT_PORT)))
    instance_name = os.getenv("MCP_INSTANCE_NAME", DEFAULT_INSTANCE_NAME)
    
    # Parse command line arguments to override env vars
    parser = argparse.ArgumentParser(description="Start MCP server with configurable options")
    parser.add_argument("--tools-dir", "-t", default=tools_dir,
                        help=f"Path to tools directory (env: MCP_TOOLS_DIR, default: {DEFAULT_TOOLS_DIR})")
    parser.add_argument("--port", "-p", type=int, default=port,
                        help=f"Port to run server on (env: MCP_PORT, default: {DEFAULT_PORT})")
    parser.add_argument("--host", default=host,
                        help=f"Host to bind server to (env: MCP_HOST, default: {DEFAULT_HOST})")
    parser.add_argument("--name", "-n", default=instance_name,
                        help="Instance name (env: MCP_INSTANCE_NAME, used for logging/identification)")
    
    return parser.parse_args()

def setup_python_path():
    """Set up the Python path to include the project root and tools directory"""
    # Add the project root to the Python path
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Add the tools directory to the Python path
    tools_dir = os.path.join(project_root, "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)

def load_tools_from_directory(directory, parent_only=False):
    """Load all tool classes from a directory
    
    Args:
        directory: Directory to load tools from
        parent_only: If True, only load tools from the parent directory, not subdirectories
    """
    tools = []
    loaded_count = 0
    
    # Ensure directory exists
    if not os.path.exists(directory):
        print(f"Directory does not exist: {directory}")
        return tools
    
    # Get Python files in the directory
    if parent_only:
        # Only get files in the parent directory
        files = [f for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f)) 
                and f.endswith('.py') 
                and not f.startswith('__')]
        
        for file in files:
            file_path = os.path.join(directory, file)
            try:
                # Load the module
                module_name = os.path.splitext(file)[0]
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find all BaseTool subclasses in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTool) and 
                            obj.__module__ == module.__name__):
                            tools.append(obj)
                            loaded_count += 1
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    else:
        # Walk through the directory and subdirectories
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    try:
                        # Load the module
                        module_name = os.path.splitext(file)[0]
                        spec = importlib.util.spec_from_file_location(module_name, file_path)
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            
                            # Find all BaseTool subclasses in the module
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    issubclass(obj, BaseTool) and 
                                    obj.__module__ == module.__name__):
                                    tools.append(obj)
                                    loaded_count += 1
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
    
    print(f"Loaded {loaded_count} tools from {directory}")
    return tools

# Alternative way of running the app with uvicorn
def setup_uvicorn_app():
    # Set up the Python path
    setup_python_path()
    
    config = get_config()
    
    # Load tools from base directory (parent level only)
    base_tools = load_tools_from_directory(DEFAULT_TOOLS_DIR, parent_only=True)
    
    # Load tools from specified directory (if different from base)
    specified_tools = []
    if config.tools_dir != DEFAULT_TOOLS_DIR and os.path.exists(config.tools_dir):
        specified_tools = load_tools_from_directory(config.tools_dir)
    
    # Combine all tools
    all_tools = base_tools + specified_tools
    
    if not all_tools:
        print("Error: No tools found in the specified directories")
        sys.exit(1)
    
    fastmcp = run_mcp(tools=all_tools, return_app=True)
    app = fastmcp.http_app(stateless_http=True, transport="sse")
    return app

# app = setup_uvicorn_app()

if __name__ == "__main__":
    # Set up the Python path
    setup_python_path()
    
    config = get_config()
    
    # Override port with MCP_PORT env var if set
    if 'MCP_PORT' in os.environ:
        config.port = int(os.environ['MCP_PORT'])
    elif 'PORT' in os.environ:
        config.port = int(os.environ['PORT'])
    
    # Load tools from base directory (parent level only)
    base_tools = load_tools_from_directory(DEFAULT_TOOLS_DIR, parent_only=True)
    
    # Load tools from specified directory (if different from base)
    specified_tools = []
    if config.tools_dir != DEFAULT_TOOLS_DIR and os.path.exists(config.tools_dir):
        specified_tools = load_tools_from_directory(config.tools_dir)
    
    # Combine all tools
    all_tools = base_tools + specified_tools
    
    if not all_tools:
        print("Error: No tools found in the specified directories")
        sys.exit(1)
    
    print(f"Starting MCP server [{config.name}]")
    print(f"  Base tools: {len(base_tools)} tools from {DEFAULT_TOOLS_DIR} (parent level only)")
    if specified_tools:
        print(f"  Additional tools: {len(specified_tools)} tools from {config.tools_dir}")
    print(f"  Total tools loaded: {len(all_tools)}")
    print(f"  Host: {config.host}")
    print(f"  Port: {config.port}")
    print(f"  Configuration source: ENV vars + CLI args")
    
    # Run MCP with all tool classes
    run_mcp(tools=all_tools, transport="sse", host=config.host, port=config.port)