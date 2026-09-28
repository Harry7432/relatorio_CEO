FROM python:3.13.14-slim@sha256:9662417aace5ae7b8e2609cce472b72a8958e134ba372808abe9cc1a0c0125e6

ARG SOURCE_REVISION
ARG DEPENDENCY_LOCK_DIGEST

RUN test -n "$SOURCE_REVISION" && test -n "$DEPENDENCY_LOCK_DIGEST"

LABEL org.opencontainers.image.revision="$SOURCE_REVISION" \
      org.opencontainers.image.source="relatorio_CEO" \
      io.relatorio-ceo.dependency-lock-digest="$DEPENDENCY_LOCK_DIGEST"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install \
        --no-cache-dir \
        --require-hashes \
        --only-binary=:all: \
        -r requirements.txt \
    && addgroup --system app \
    && adduser --system --ingroup app --home /app app

COPY --chown=app:app app.py ./
COPY --chown=app:app src ./src

USER app
