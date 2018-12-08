FROM python:2
WORKDIR "/root/"
COPY *.py /root/
ENTRYPOINT ["python","-u","server.py"]