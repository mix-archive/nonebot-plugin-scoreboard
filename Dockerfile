FROM python:slim

COPY pyproject.toml README.md bot.py /project/
COPY src/ /project/src

WORKDIR /project
RUN --mount=type=cache,target=/tmp \
    pip install -e . --cache-dir /tmp

ARG SUPERUSERS
ENV HOST=0.0.0.0 \
    PORT=8080 \
    SUPERUSERS=$SUPERUSERS

RUN useradd -M -s /bin/bash bot && \
    mkdir /project/data && \
    chown -R bot:bot /project/data

CMD ["/bin/bash", "-c", "\
    echo $FLAG > /flag && \
    unset FLAG && \
    exec su bot -c 'python bot.py'"]