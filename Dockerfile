FROM python:3-alpine
# https://docs.authlib.org/en/latest/basic/install.html#pip-install-authlib
# https://cryptography.io/en/latest/installation/#alpine
RUN apk add gcc musl-dev python3-dev libffi-dev openssl-dev
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
