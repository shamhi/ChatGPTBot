FROM python:3.10-slim

ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -U -r requirements.txt

COPY . .

CMD ["python3", "main.py"]