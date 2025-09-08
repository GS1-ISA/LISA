# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements files from the project root into the container
COPY requirements.txt requirements-dev.txt /app/

# Install uv and then the dependencies
RUN pip install uv && \
    uv pip install --no-cache-dir -r requirements.txt && \
    uv pip install --no-cache-dir -r requirements-dev.txt

# Copy the application source code into the container
# Use the monorepo's src to make the API server available
COPY src /app/src

# Expose the port the app runs on
EXPOSE 8787

# Define the command to run the application
CMD ["uvicorn", "src.api_server:app", "--host", "0.0.0.0", "--port", "8787"]

# Add a healthcheck (no curl dependency)
HEALTHCHECK --interval=30s --timeout=10s CMD python - <<'PY' || exit 1
import sys, urllib.request
for url in ("http://localhost:8787/metrics", "http://localhost:8787/"):
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            if r.status == 200:
                sys.exit(0)
    except Exception:
        pass
sys.exit(1)
PY
