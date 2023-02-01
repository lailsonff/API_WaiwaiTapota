FROM python:3.8.10-slim

RUN apt-get --yes --quiet update && \
    apt-get --yes --quiet install gcc && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN groupadd -r backend && useradd --no-log-init -r -m -g backend backend
USER backend

RUN mkdir -p /home/backend/project
WORKDIR /home/backend

ENV VIRTUAL_ENV=/home/backend/venv
RUN python3 -m venv ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools wheel pip-tools

COPY --chown=backend:backend requirements.in .

RUN pip-compile --output-file=requirements.txt requirements.in && pip install -r requirements.txt

COPY --chown=backend:backend . ./project