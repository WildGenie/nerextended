# Force rebuild - 2026-01-16 04:52
# Use Python 3.11 slim bookworm (stable)
FROM python:3.11-slim-bookworm

# Set environment variables
ENV NB_USER=jovyan \
    NB_UID=1000 \
    HOME=/home/jovyan \
    JAVA_HOME=/usr/lib/jvm/default-java \
    DOTNET_ROOT=/usr/share/dotnet \
    PATH="/usr/share/dotnet:${PATH}:/home/jovyan/.local/bin" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jdk \
    curl \
    ca-certificates \
    build-essential \
    libicu-dev \
    && curl -sSL https://dot.net/v1/dotnet-install.sh | bash /dev/stdin --channel 9.0 --install-dir /usr/share/dotnet \
    && ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create user
RUN useradd -m -u ${NB_UID} ${NB_USER}
WORKDIR ${HOME}
USER ${NB_USER}

# Copy requirements
COPY --chown=${NB_USER}:${NB_USER} requirements.txt /tmp/requirements.txt

# Optimized Pip installation
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy source code
COPY --chown=${NB_USER}:${NB_USER} . ${HOME}

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"

# Pre-build Nuve Wrapper
RUN cd nuve_wrapper && dotnet build -c Release

# Expose port
EXPOSE 7860

# Entrypoint
ENTRYPOINT ["streamlit", "run", "Demo.py", "--server.port=7860", "--server.address=0.0.0.0"]
