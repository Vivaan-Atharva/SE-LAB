import sys

from game import Battleship

if __name__ == "__main__":
    # Optional seed for a reproducible layout: python main.py 42
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else None
    try:
        Battleship(seed).run()
    except (KeyboardInterrupt, EOFError):
        print("\nBye.")
