# Stage 1: Build the requirements.txt using Poetry
FROM python:3.12-slim AS builder

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="${PATH}:/root/.local/bin"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Copy only the poetry.lock/pyproject.toml to leverage Docker cache
WORKDIR /app
COPY pyproject.toml poetry.lock /app/

# Install dependencies and create requirements.txt
RUN poetry self add poetry-plugin-export && poetry export --format=requirements.txt --output=requirements.txt --only=main --without-hashes

# Stage 2: Install dependencies and run the Django application
FROM python:3.12-slim AS runner

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create a non-root user
RUN useradd -ms /bin/bash appuser

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy the generated requirements.txt from the builder stage
WORKDIR /app
COPY --from=builder /app/requirements.txt /app/

# Install application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# The port the application will listen on
EXPOSE 8000

# Run startup script
CMD ["./docker-entrypoint.sh"]
