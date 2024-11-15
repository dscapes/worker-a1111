# Базовый образ
FROM python:3.9-slim

# Установка переменных окружения
ARG CIVITAI_TOKEN
ENV CIVITAI_TOKEN=${CIVITAI_TOKEN}

# Use bash shell with pipefail option
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Создаем рабочую директорию
WORKDIR /

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .

# Update and upgrade the system packages (Worker Template)
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install --yes --no-install-recommends \
    build-essential vim git wget ffmpeg libsm6 libxext6

# Update and upgrade the system packages (Worker Template)
COPY builder/setup.sh /setup.sh
RUN /bin/bash /setup.sh && \
    rm /setup.sh

# Install Python dependencies (Worker Template)
COPY builder/requirements.txt /requirements.txt
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

# Копируем скрипт wrapper.py и другие нужные файлы в контейнер
COPY src/wrapper.py .

# Открываем необходимые порты (если нужно)
EXPOSE 8080

# Add src files (Worker Template)
ADD src .

CMD python3 -u /wrapper.py --civitai_token=${CIVITAI_TOKEN}
# CMD ["python", "src/wrapper.py"]