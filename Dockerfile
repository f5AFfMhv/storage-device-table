#FROM python:3.8.5
FROM python_sdm:latest
WORKDIR /app
COPY html /app/html/
COPY img /app/img/
COPY scripts /app/scripts/
COPY app.py /app
COPY graphs.py /app
COPY clean.db /app/servers.db
# RUN pip3 install --trusted-host pypi.python.org Flask
# RUN pip3 install --trusted-host pypi.python.org requests
# RUN pip3 install --trusted-host pypi.python.org plotly
# RUN pip3 install --trusted-host pypi.python.org pandas
# RUN pip3 install --trusted-host pypi.python.org ipython
# RUN pip3 install --trusted-host pypi.python.org nbformat
EXPOSE 5000
CMD ["python3", "app.py"]