FROM python:3.10

WORKDIR /code

COPY ./api/requirements.txt /code/api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/api/requirements.txt

COPY ./api /code/api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
