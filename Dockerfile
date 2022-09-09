FROM python:3.10-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY caus.py caus.py
COPY controller.py controller.py
COPY elasticity.py elasticity.py
COPY prometheusclient.py prometheusclient.py
CMD [ "python3", "-u" ,"controller.py" ]
