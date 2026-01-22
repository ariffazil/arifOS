"""Dispatcher for 777 forge command."""
import sys
import argparse
from arifos_clip.aclip.core import session as session_core
from importlib import util

def main(argv=None):
    parser = argparse.ArgumentParser(prog="777", description="Execute A CLIP stage 777 - forge")
    parser.add_argument("verb", choices=["forge"], help="Stage verb (must be 'forge')")
    parser.add_argument("input", nargs="*", help="Forge context or confirmation")
    parser.add_argument("--json", action="store_true", help="Output result in JSON")
    args = parser.parse_args(argv)
    sess = session_core.Session.load_or_init()
    stage_file = session_core.get_cli_stage_file("777_forge.py")
    spec = util.spec_from_file_location("aclip.cli.777_forge", stage_file)
    if spec is None:
        print("Error: Stage module file not found:", stage_file, file=sys.stderr)
        return 88
    stage_mod = util.module_from_spec(spec)
    spec.loader.exec_module(stage_mod)
    if hasattr(stage_mod, "run_stage"):
        exit_code = stage_mod.run_stage(sess, args)
    elif hasattr(stage_mod, "main"):
        exit_code = stage_mod.main(args)
    else:
        print("Error: Stage module has no entry point", file=sys.stderr)
        return 88
    sess.save()
    return exit_code

if __name__ == "__main__":
    sys.exit(main())
