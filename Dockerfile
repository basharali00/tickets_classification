FROM python:3.14-slim AS base

WORKDIR /app

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Exact pins only. Regenerate requirements/*.txt by hand (command in each header).
COPY requirements/requirements.txt requirements/requirements.txt
RUN pip install --no-cache-dir -r requirements/requirements.txt

EXPOSE 80
COPY --chmod=755 ./start.sh /start.sh
CMD ["/start.sh"]


FROM base AS prod

ENV ENVIRONMENT=prod
COPY ./alembic.ini .
COPY ./migrations ./migrations
COPY ./packages ./packages
COPY ./dependencies ./dependencies

# Commit metadata must not invalidate reusable filesystem layers.
ARG RELEASE_SHA=unknown
ENV RELEASE_SHA=$RELEASE_SHA


FROM base AS test

ENV ENVIRONMENT=test
COPY requirements/requirements-test.txt requirements/requirements-test.txt
RUN pip install --no-cache-dir -r requirements/requirements-test.txt

COPY ./pyproject.toml .
COPY ./alembic.ini .
COPY ./migrations ./migrations
COPY ./packages ./packages
COPY ./dependencies ./dependencies

CMD ["pytest"]


FROM test AS local

# Source is bind-mounted by docker-compose; start.sh reloads on change.
ENV ENVIRONMENT=local \
    RELOAD=true
CMD ["/start.sh"]
