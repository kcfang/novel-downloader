FROM python:3.7

ENV DOCKER_CONTAINER=1
ENV DJANGO_ENV=production

ADD requirements.txt /
RUN pip install -r /requirements.txt

EXPOSE 9527
CMD ["uwsgi", "--ini", "/Projects/novel/novel.ini"]
