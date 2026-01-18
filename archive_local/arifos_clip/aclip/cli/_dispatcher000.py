"""Dispatcher for 000 void command."""
import sys
import argparse
# Import session management
from arifos_clip.aclip.core import session as session_core
# We will dynamically load the stage module by file path because module name is numeric
from importlib import util

def main(argv=None):
    parser = argparse.ArgumentParser(prog="000", description="Execute A CLIP stage 000 - void")
    parser.add_argument("verb", choices=["void"], help="Stage verb (must be 'void')")
    parser.add_argument("task", nargs="+", help="Task description for the void stage")
    parser.add_argument("--json", action="store_true", help="Output result in JSON")
    args = parser.parse_args(argv)
    # Initialize or load session
    sess = session_core.Session.load_or_init()
    # Dynamically import the stage module 000_void.py
    stage_file = session_core.get_cli_stage_file("000_void.py")
    spec = util.spec_from_file_location("aclip.cli.000_void", stage_file)
    if spec is None:
        print("Error: Stage module file not found:", stage_file, file=sys.stderr)
        return 88  # treat as hold if missing critical component
    stage_mod = util.module_from_spec(spec)
    spec.loader.exec_module(stage_mod)
    # Run the stage logic function if available
    if hasattr(stage_mod, "run_stage"):
        exit_code = stage_mod.run_stage(sess, args)
    elif hasattr(stage_mod, "main"):
        # If stage file has its own main function, call it (not used in this design)
        exit_code = stage_mod.main(args)
    else:
        print("Error: Stage module has no entry point", file=sys.stderr)
        return 88
    # Save session after stage execution (if modified)
    sess.save()
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
