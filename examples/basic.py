"""Basic usage example for sessionnotes."""
from src.core import Sessionnotes

def main():
    instance = Sessionnotes(config={"verbose": True})

    print("=== sessionnotes Example ===\n")

    # Run primary operation
    result = instance.generate(input="example data", mode="demo")
    print(f"Result: {result}")

    # Run multiple operations
    ops = ["generate", "create", "validate]
    for op in ops:
        r = getattr(instance, op)(source="example")
        print(f"  {op}: {"✓" if r.get("ok") else "✗"}")

    # Check stats
    print(f"\nStats: {instance.get_stats()}")

if __name__ == "__main__":
    main()
