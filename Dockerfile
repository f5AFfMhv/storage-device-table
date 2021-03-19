FROM python:3.8.5
WORKDIR /app
COPY templates /app/templates/
COPY img /app/img/
COPY scripts/SDT-ansible-playbook.yml /app/scripts/SDT-ansible-playbook.yml
COPY scripts/SDT-linux-agent.sh /app/scripts/SDT-linux-agent.sh
COPY scripts/SDT-windows-agent.ps1 /app/scripts/SDT-windows-agent.ps1
COPY app.py /app
COPY graphs.py /app
COPY SDT.db /app/SDT.db
RUN pip3 install --trusted-host pypi.python.org Flask
RUN pip3 install --trusted-host pypi.python.org requests
RUN pip3 install --trusted-host pypi.python.org plotly
RUN pip3 install --trusted-host pypi.python.org pandas
RUN pip3 install --trusted-host pypi.python.org ipython
RUN pip3 install --trusted-host pypi.python.org nbformat
EXPOSE 5000
CMD ["python3", "app.py"]