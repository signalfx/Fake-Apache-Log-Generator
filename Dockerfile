FROM python:3-alpine AS build
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk --no-cache add build-base gcc openblas-dev \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3-alpine AS lint
RUN python -m pip install flake8 \
    && mkdir /source
COPY . /source
RUN flake8 --max-line-length=120 /source

FROM python:3-alpine
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories \
    && apk --no-cache add openblas \
    && mkdir -p /logs
COPY --from=build /usr/local/lib /usr/local/lib
COPY apache-fake-log-gen.py /usr/src/app/
ENTRYPOINT [ "python", "/usr/src/app/apache-fake-log-gen.py" ]