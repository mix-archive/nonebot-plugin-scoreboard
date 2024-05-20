FROM python:slim AS builder

RUN --mount=type=tmpfs,target=/root/.cache/pip \
    pip install --upgrade pdm

COPY pyproject.toml pdm.lock README.md /project/
COPY src/ /project/src

WORKDIR /project
ENV PDM_CHECK_UPDATE=false
RUN pdm build

FROM python:slim

RUN useradd -m -s /bin/bash bot

RUN --mount=type=bind,from=builder,source=/project/dist,target=/project/dist \
    --mount=type=tmpfs,target=/root/.cache/pip \
    pip install /project/dist/*.whl && \
    pip install nb-cli

COPY pyproject.toml /home/bot/
WORKDIR /home/bot

ARG SUPERUSERS
ENV HOST=0.0.0.0 \
    PORT=8080 \
    SUPERUSERS=$SUPERUSERS
CMD ["/bin/bash", "-c", "\
    echo $FLAG > /flag && \
    unset FLAG && \
    su bot -c 'nb run'"]