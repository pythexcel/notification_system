FROM python:3.6

WORKDIR /workspace

COPY app /workspace/app

COPY .env /workspace
COPY mail_templates.py /workspace
COPY mail_variables.py /workspace
COPY recruit_slack.py /workspace
COPY recruit_templates.py /workspace
COPY slack_messages.py /workspace
COPY requirements.txt /workspace

RUN pip install -r requirements.txt



ENV FLASK_APP=app
ENV FLASK_ENV=production


RUN apt-get update && \
	apt-get install supervisor -y && \
    apt-get -y autoclean && \
	rm -rf /var/cache/apk/*

RUN mkdir /workspace/logs

COPY ./docker/supervisor/conf.d/notify.conf /etc/supervisor/conf.d/notify.conf

CMD ["/usr/bin/supervisord"]

RUN apt-get install -y debconf-utils
ENV TZ=Asia/Kolkata
RUN echo $TZ > /etc/timezone
# RUN rm /etc/localtime
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y tzdata
RUN dpkg-reconfigure --frontend noninteractive tzdata
RUN apt-get clean

RUN pytest

