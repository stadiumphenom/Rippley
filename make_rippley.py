#!/usr/bin/env python3
"""
Rippley Application Entry Point
Neo-Glyph Agent System with FastAPI Web Interface

This script serves as the main entry point for the Rippley application,
providing both development and production startup capabilities.
"""

import os
import sys
import argparse
import logging
from typing import Optional

def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('rippley.log')
        ]
    )

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    required_packages = ['fastapi', 'uvicorn', 'jinja2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Error: Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def initialize_agent_core() -> None:
    """Initialize the agent core system."""
    try:
        from agent_core import AgentFactory, TaskRunner, MemoryLink
        from agent_core.agent_factory import agent_factory
        from agent_core.task_runner import task_runner
        from agent_core.memory_link import memory_manager
        
        logger = logging.getLogger(__name__)
        logger.info("Initializing agent core systems...")
        
        # Initialize basic agent types
        # TODO: Register specific Neo-Glyph agent types here
        logger.info("Agent factory initialized")
        logger.info("Task runner initialized") 
        logger.info("Memory manager initialized")
        
        logger.info("Agent core systems ready")
        
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to initialize agent core: {e}")
        sys.exit(1)

def load_configuration() -> dict:
    """Load application configuration from config files."""
    import json
    config = {}
    
    config_files = [
        ('glyph_spec', 'config/glyph_spec.json'),
        ('nl_rules', 'config/nl_rules.json')
    ]
    
    for config_name, config_path in config_files:
        try:
            with open(config_path, 'r') as f:
                config[config_name] = json.load(f)
        except FileNotFoundError:
            logging.warning(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {config_path}: {e}")
    
    return config

def run_development_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True) -> None:
    """Run the development server with hot reload."""
    import uvicorn
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting development server on {host}:{port}")
    
    try:
        uvicorn.run(
            "rippley_viewer.app:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Development server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        sys.exit(1)

def run_production_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 4) -> None:
    """Run the production server with multiple workers."""
    import uvicorn
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting production server on {host}:{port} with {workers} workers")
    
    try:
        uvicorn.run(
            "rippley_viewer.app:app",
            host=host,
            port=port,
            workers=workers,
            log_level="warning"
        )
    except KeyboardInterrupt:
        logger.info("Production server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start production server: {e}")
        sys.exit(1)

def show_system_info() -> None:
    """Display system information and status."""
    print("🌊 Rippley - Neo-Glyph Agent System")
    print("=" * 40)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    
    # Check agent core modules
    try:
        from agent_core import __version__
        print(f"Agent Core Version: {__version__}")
    except ImportError:
        print("Agent Core: Not available")
    
    # Check configuration
    config = load_configuration()
    print(f"Configuration Files Loaded: {len(config)}")
    
    print("\nAvailable Commands:")
    print("  python make_rippley.py run        - Start development server")
    print("  python make_rippley.py prod       - Start production server")
    print("  python make_rippley.py info       - Show system information")
    print("  python make_rippley.py test       - Run system tests")

def run_tests() -> None:
    """Run basic system tests."""
    logger = logging.getLogger(__name__)
    logger.info("Running system tests...")
    
    # Test 1: Import core modules
    try:
        from agent_core import AgentFactory, TaskRunner, MemoryLink
        print("✓ Agent core modules import successfully")
    except ImportError as e:
        print(f"✗ Agent core import failed: {e}")
        return
    
    # Test 2: Configuration loading
    config = load_configuration()
    if config:
        print("✓ Configuration files loaded successfully")
    else:
        print("⚠ No configuration files found")
    
    # Test 3: FastAPI app
    try:
        from rippley_viewer.app import app
        print("✓ FastAPI application loads successfully")
    except ImportError as e:
        print(f"✗ FastAPI application import failed: {e}")
        return
    
    # Test 4: Agent factory basic functionality
    try:
        factory = AgentFactory()
        agent = factory.create_agent("test", {"id": "test_agent"})
        print("✓ Agent factory creates agents successfully")
    except Exception as e:
        print(f"✗ Agent factory test failed: {e}")
    
    print("\nSystem tests completed!")

def main() -> None:
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="Rippley - Neo-Glyph Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'command',
        choices=['run', 'prod', 'info', 'test'],
        default='run',
        nargs='?',
        help='Command to execute (default: run)'
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind to (default: 8000)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=4,
        help='Number of worker processes for production (default: 4)'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--no-reload',
        action='store_true',
        help='Disable auto-reload in development mode'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize agent core if not running info command
    if args.command != 'info':
        initialize_agent_core()
        load_configuration()
    
    # Execute command
    if args.command == 'run':
        run_development_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    elif args.command == 'prod':
        run_production_server(
            host=args.host,
            port=args.port,
            workers=args.workers
        )
    elif args.command == 'info':
        show_system_info()
    elif args.command == 'test':
        run_tests()

if __name__ == "__main__":
    main()