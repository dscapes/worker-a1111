FROM python:3.9-slim

ARG CIVITAI_TOKEN
ENV CIVITAI_TOKEN=${CIVITAI_TOKEN}

# Use bash shell with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

WORKDIR /

COPY requirements.txt .

# Update and upgrade the system packages (Worker Template)
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install --yes --no-install-recommends \
    build-essential vim git wget ffmpeg libsm6 libxext6

# Update and upgrade the system packages (Worker Template)
# COPY builder/setup.sh /setup.sh
# RUN /bin/bash /setup.sh && \
#     rm /setup.sh

# Install Python dependencies (Worker Template)
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

# Add src files (Worker Template)
ADD src .

# EXPOSE 8080

CMD python3 -u /wrapper.py --civitai_token=${CIVITAI_TOKEN}
# CMD ["python", "src/wrapper.py"]