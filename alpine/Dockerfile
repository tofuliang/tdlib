FROM alpine:latest

ARG TD_COMMIT=24893faf7

ENV LANG en_US.UTF-8
ENV TZ UTC

RUN apk update && \
    apk upgrade && \
    apk add --update --virtual .build-deps \
        build-base \
        ca-certificates \
        ccache \
        cmake \
        git \
        gperf \
        linux-headers \
        openssl-dev \
        php \
        php-ctype \
        readline-dev \
        zlib-dev && \
    git clone "https://github.com/tdlib/td.git" /src && \
    cd /src && \
    git checkout ${TD_COMMIT} && \
    mkdir ./build && \
    cd ./build && \
    cmake \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX:PATH=/usr/local \
        .. && \
    cmake --build . -j`grep -c ^processor /proc/cpuinfo` --target prepare_cross_compiling && \
    cd .. && \
    php SplitSource.php && \
    cd build && \
    cmake --build . -j`grep -c ^processor /proc/cpuinfo` --target install && \
    apk del .build-deps && \
    cd / && rm -fr /src
RUN apk add zlib-static openssl-libs-static && \
    ls -lah /usr/local
