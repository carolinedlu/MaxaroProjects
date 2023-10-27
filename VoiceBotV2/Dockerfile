# Use Python 3.11.4 as the base image
FROM python:3.11.4

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system libraries for audio processing
RUN apt-get update && apt-get install -y \
    libasound2          \
    libnss3             \
    libnspr4            \
    libatk1.0-0         \
    libatk-bridge2.0-0  \
    libcups2            \
    libdrm2             \
    libxkbcommon0       \
    libxcomposite1      \
    libxdamage1         \
    libxfixes3          \
    libxrandr2          \   
    libgbm1             \
    libpango-1.0-0      \
    libcairo2           \
    libasound2          \
    libatspi2.0-0       \
    libwayland-client0  \
    git

RUN git clone https://github.com/BenjaminGraziadei223946/MaxaroProjects/tree/main/VoiceBotV2

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Run streamlit when the container launches
CMD ["streamlit", "run", "VoiceBotV2.py"]
