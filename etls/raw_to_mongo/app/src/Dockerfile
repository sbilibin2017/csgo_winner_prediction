# base image
FROM python:3.10-slim

# environment variables
ENV APP_HOME=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# create app directory
WORKDIR ${APP_HOME}

RUN adduser --system --no-create-home default_user



# install dependancies
RUN apt-get update && \
    apt-get install -y gettext && \
    apt install -y ncat && \
    python -m pip install --upgrade pip && \    
    pip3 install poetry

# copy files
COPY . ${APP_HOME}

# install dependancies
RUN poetry config virtualenvs.create false
RUN poetry install

USER default_user

# changing mode of entrypoint
RUN chmod +x ./docker-entrypoint.sh

EXPOSE ${APP_PORT}

# run script 
ENTRYPOINT ["./docker-entrypoint.sh"]