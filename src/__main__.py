"""CLI for sessionnotes."""
import sys, json, argparse
from .core import Sessionnotes

def main():
    parser = argparse.ArgumentParser(description="SessionNotes — AI Therapy Note Generator. Generate SOAP notes from therapy session recordings.")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = Sessionnotes()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.generate(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"sessionnotes v0.1.0 — SessionNotes — AI Therapy Note Generator. Generate SOAP notes from therapy session recordings.")

if __name__ == "__main__":
    main()
