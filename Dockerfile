FROM python:3.8.5
WORKDIR /app
ADD . /app
RUN pip3 install --trusted-host pypi.python.org Flask
RUN pip3 install --trusted-host pypi.python.org requests
EXPOSE 5000
CMD ["python3", "app.py"]