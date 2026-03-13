"""
List all available FastAPI routes
"""
import sys
sys.path.insert(0, 'app')

from main import app

print("Available Routes:")
print("-" * 80)
for route in app.routes:
    if hasattr(route, 'methods'):
        methods = ', '.join(route.methods)
        print(f"{methods:10} {route.path}")
print("-" * 80)
