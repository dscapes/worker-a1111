FROM ghcr.io/ai-dock/stable-diffusion-webui:latest

ENV DEBIAN_FRONTEND=noninteractive

ARG CIVITAI_TOKEN
ENV CIVITAI_TOKEN=${CIVITAI_TOKEN}

# Копируем ваши дополнительные файлы
COPY builder/setup.sh /setup.sh
RUN /bin/bash /setup.sh && \
    rm /setup.sh

COPY builder/requirements.txt /requirements.txt
RUN python3 -m pip install --upgrade -r /requirements.txt --no-cache-dir && \
    rm /requirements.txt

# Добавляем ваш код
ADD src .

# Добавляем конфиг для нашего wrapper в supervisor
COPY <<EOF /etc/supervisor/conf.d/wrapper.conf
[program:wrapper]
command=python3 -u /wrapper.py --civitai_token=%(ENV_CIVITAI_TOKEN)s
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
priority=1
autostart=true
autorestart=true
startsecs=0
EOF

# Оставляем оригинальную точку входа
CMD ["init.sh"]