# Same as app.py but runs on port 8000
# Copy all content from app.py and change the port

import sys
from pathlib import Path

# Copy the exact same content as app.py
with open(Path(__file__).parent / "app.py", "r") as f:
    content = f.read()

# Replace the port
content = content.replace("port=8080", "port=8000")
content = content.replace("localhost:8080", "localhost:8000")

# Write to a temp file and execute
exec(content.replace('if __name__ == "__main__":', 'if True:').replace('uvicorn.run(', 'import uvicorn; uvicorn.run('))