import os
import sys
import argparse

# Add the project root to sys.path so we can import apps
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.core.output import setup_output, print_error
from tools.core.registry import get_all_commands, get_command

# Import all commands so they register themselves
import tools.commands.ops
import tools.commands.testing
import tools.commands.code
import tools.commands.devops
import tools.commands.database
import tools.commands.security

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional CLI Tool for Handcrafts Project")
    parser.add_argument("command", choices=get_all_commands(), help="Command to execute")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--quiet", action="store_true", help="Suppress all non-error output")
    parser.add_argument("--yes", action="store_true", help="Auto-confirm dangerous actions (Not allowed in production)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate data-altering commands without saving changes")
    
    args, unknown = parser.parse_known_args()
    
    setup_output(verbose=args.verbose, quiet=args.quiet)
    
    # Pass remaining arguments to the subcommand via sys.argv
    sys.argv = [sys.argv[0]] + unknown
    
    func = get_command(args.command)
    
    if not func:
        print_error(f"Command '{args.command}' not found.")
        sys.exit(1)
        
    try:
        # Pass the parsed args object so commands can check --yes or --dry-run
        exit_code = func(args)
        if exit_code is None:
            exit_code = 0
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print_error("Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unhandled exception: {e}")
        sys.exit(1)
