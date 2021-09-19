# Made using example from 
# https://github.com/GoogleContainerTools/distroless/blob/main/examples/python3-requirements/Dockerfile


# Build a virtualenv using the appropriate Debian release
# * Install python3-venv for the built-in Python3 venv module (not installed by default)
# * Install gcc libpython3-dev to compile C Python modules
# * Update pip to support bdist_wheel
FROM debian:buster-slim AS build
RUN apt-get update && \
    apt-get install --no-install-suggests --no-install-recommends --yes python3-venv gcc libpython3-dev && \
    python3 -m venv /venv && \
    /venv/bin/pip install --upgrade pip

# Build the virtualenv as a separate step: Only re-execute this step when requirements.txt changes
FROM build AS build-venv
# metadata
LABEL dockerfile.version="2"
LABEL software="SDT"
LABEL software.version="1.2"
LABEL description="RESTful API for monitoring storage device usage"
LABEL website="https://github.com/f5AFfMhv/storage-device-table"
LABEL license="https://github.com/f5AFfMhv/storage-device-table/blob/master/COPYING"
LABEL maintainer="Martynas J."
LABEL maintainer.email="mjankunas@gmail.com"

COPY requirements.txt /requirements.txt
RUN /venv/bin/pip install --disable-pip-version-check -r /requirements.txt

# Copy the virtualenv into a distroless image
FROM gcr.io/distroless/python3-debian10
EXPOSE 5000
WORKDIR /app
COPY --from=build-venv /venv /venv
COPY . /app
ENTRYPOINT ["/venv/bin/python3", "app.py"]
