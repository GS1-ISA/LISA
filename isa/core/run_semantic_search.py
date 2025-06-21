import sys
import json
from isa.core.search_interface import semantic_search

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No query provided."}))
        sys.exit(1)

    query = sys.argv[1]
    try:
        results = semantic_search(query)
        print(json.dumps({"results": results}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)