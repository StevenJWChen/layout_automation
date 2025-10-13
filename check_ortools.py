#!/usr/bin/env python3
import sys

try:
    from ortools.sat.python import cp_model
    print("SUCCESS: OR-Tools imported successfully!")
    sys.exit(0)
except ImportError as e:
    print(f"IMPORT ERROR: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"OTHER ERROR: {type(e).__name__}: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(2)
