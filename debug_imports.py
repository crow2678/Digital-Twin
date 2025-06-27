# Run this to see what classes are available in your SDK version
import azure.search.documents.indexes.models as models
import inspect

print("Available classes in azure.search.documents.indexes.models:")
for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and ('Vector' in name or 'Hnsw' in name or 'Algorithm' in name):
        print(f"  {name}")

print("\nAll available classes:")
for name, obj in inspect.getmembers(models):
    if inspect.isclass(obj) and not name.startswith('_'):
        print(f"  {name}")