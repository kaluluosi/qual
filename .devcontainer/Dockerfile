FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

ENV PYTHONUNBUFFERED 1

# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# 这里不能用USER，必须用root操作
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    nodejs \
    npm

ARG USER=vscode
USER $USER
ARG HOME="/home/${USER}"

ENV PATH="${HOME}/.local/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -\
    # && export PATH="${HOME}/.local/bin:$PATH" \
    && poetry config virtualenvs.in-project true
