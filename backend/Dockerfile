# Stage 1: Build the dependency layer
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# This will create the virtualenv in .venv
RUN poetry config virtualenvs.in-project true

# Copy only the files needed for dependency installation
COPY pyproject.toml /app/

# Install dependencies
# --no-root: Don't install the project itself, only the dependencies
RUN poetry install --no-root

# Stage 2: Build the final application image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy the virtualenv from the builder
COPY --from=builder /app/.venv ./.venv

# Copy the application code
COPY . /app/

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
