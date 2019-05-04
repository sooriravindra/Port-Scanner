FROM python:3.6

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND  db+mysql://root:123@db:3306/test
ENV MYSQL_HOST db

ENV HOST 0.0.0.0
ENV PORT 5001
ENV DEBUG true

COPY . /api
WORKDIR /api

# install requirements
RUN pip install -r requirements.txt

# expose the app port
EXPOSE 5001

RUN pip install gunicorn
# run the app server
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "3", "app:app"]

