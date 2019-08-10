FROM python:3.7
ADD requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
ADD project.py /project.py
ADD web /web
ADD templates /templates
ENTRYPOINT ["python3", "project.py"]