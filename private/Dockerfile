FROM python:slim AS base

RUN apt-get update && \
    apt-get install -y sudo tini bash inotify-tools unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md bot.py /project/
COPY src/ /project/src

WORKDIR /project
RUN --mount=type=cache,target=/tmp \
    pip install -e . --cache-dir /tmp && \
    pip install requests --cache-dir /tmp

ARG SUPERUSERS
ENV HOST=0.0.0.0 \
    PORT=80 \
    SUPERUSERS=$SUPERUSERS

RUN useradd -M -s /bin/bash bot && \
    mkdir /project/data && \
    chown -R bot:bot /project/data

EXPOSE 80/tcp
COPY entrypoint.sh /entrypoint.sh
CMD ["tini", "--", "/entrypoint.sh"]

FROM base AS private

COPY ./private/easter/stream.pcapng /root/stream.pcapng
RUN chown root:root /root/stream.pcapng && \
    chmod 400 /root/stream.pcapng && \
    echo "bot ALL=(ALL) NOPASSWD: $(which python)" >> /etc/sudoers.d/bot && \
    echo "there maybe some easter egg in somewhere" > /project/hint.txt