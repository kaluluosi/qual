FROM alpine:latest

RUN apk update \ 
    && apk add \
    make \
    git \
    python3 \
    py3-pip \
    && python -m pip install -U pip \
    && pip install poetry 

ENTRYPOINT [ "bash" ]