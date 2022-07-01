FROM python:3.9

WORKDIR /workspace
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "api.py" ]