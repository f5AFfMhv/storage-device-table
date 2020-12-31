FROM python:3.8.5
WORKDIR /app
ADD . /app
RUN pip3 install --trusted-host pypi.python.org Flask
CMD ["python3", "api.py"]