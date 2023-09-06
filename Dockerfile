# Use a smaller base image
FROM python:3.10-slim-buster

# Set environment variables to prevent prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and clean up apt cache in a single RUN step
RUN apt-get update -y && \
    apt-get install -y tesseract-ocr libtesseract-dev libreoffice poppler-utils default-jdk && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a directory for the Tesseract trained data and copy it
RUN mkdir -p /usr/share/tesseract-ocr/5/tessdata/
COPY eng.traineddata /usr/share/tesseract-ocr/5/tessdata/eng.traineddata

# Set the working directory
WORKDIR /app

# Copy only the necessary files for dependency installation
COPY pyproject.toml poetry.lock __init__.py ./

# Install poetry and project dependencies
RUN pip install --upgrade poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-dev

# Copy the application source code
COPY src ./src

# Set appropriate permissions for the application directory
RUN chmod 777 -R /app/src

# Define the command to run your application
CMD ["/app/.venv/bin/python", "src/main.py"]
