FROM docker.io/mimove/tickettrackr-extract-load-base-dependecies:1 

ARG BUILD_DATE
ARG VCS_REF
LABEL org.label-schema.build-date=${BUILD_DATE} \
        org.label-schema.name="tickettrackr"\
        org.label-schema.vcs-ref=${VCS_REF} \
        org.label-schema.license=MIT

COPY docker/scripts /app/scripts
COPY ./cli /app/cli
COPY ./requirements /app/requirements

WORKDIR /app/cli

ENV PYTHONPATH=/app/cli
ENV PYTHONUNBUFFERED=1

####################
## continue with the rest of the Dockerfile
## what/ how to run docker with .env file
####################

