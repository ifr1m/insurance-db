FROM python:3.8.12-slim-buster as env-setup

# https://github.com/dooman87/imagemagick-docker/blob/master/Dockerfile.buster
ENV DEBIAN_FRONTEND=noninteractive

ARG IM_VERSION=7.1.0-16
ARG LIB_HEIF_VERSION=1.12.0
ARG LIB_AOM_VERSION=3.2.0
ARG LIB_WEBP_VERSION=1.2.1
ARG GS_VERSION=9.55.0

RUN apt-get -y update && \
    apt-get -y upgrade && \
    apt-get install -y git make gcc pkg-config autoconf curl g++ \
    # libaom
    yasm cmake \
    # libheif
    libde265-0 libde265-dev libjpeg62-turbo libjpeg62-turbo-dev x265 libx265-dev libtool \
    # IM
    libpng16-16 libpng-dev libjpeg62-turbo libjpeg62-turbo-dev libgomp1 libxml2-dev libxml2-utils libtiff-dev libfontconfig1-dev libfreetype6-dev && \
    #Building ghostscript
    curl -L https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs9550/ghostscript-${GS_VERSION}.tar.gz -o ghostscript.tar.gz && \
    tar -xzvf ghostscript.tar.gz && cd ghostscript-${GS_VERSION}/ &&  \
    ./configure && make && make install && \
    ldconfig /usr/local/lib && \
    cd ../ && rm -rf ghostscript-${GS_VERSION} && rm ghostscript.tar.gz &&\
    # Building libwebp
    git clone https://chromium.googlesource.com/webm/libwebp && \
    cd libwebp && git checkout v${LIB_WEBP_VERSION} && \
    ./autogen.sh && ./configure --enable-shared --enable-libwebpdecoder --enable-libwebpdemux --enable-libwebpmux --enable-static=no && \
    make && make install && \
    ldconfig /usr/local/lib && \
    cd ../ && rm -rf libwebp && \
    # Building libaom
    git clone https://aomedia.googlesource.com/aom && \
    cd aom && git checkout v${LIB_AOM_VERSION} && cd .. && \
    mkdir build_aom && \
    cd build_aom && \
    cmake ../aom/ -DENABLE_TESTS=0 -DBUILD_SHARED_LIBS=1 && make && make install && \
    ldconfig /usr/local/lib && \
    cd .. && \
    rm -rf aom && \
    rm -rf build_aom && \
    # Building libheif
    curl -L https://github.com/strukturag/libheif/releases/download/v${LIB_HEIF_VERSION}/libheif-${LIB_HEIF_VERSION}.tar.gz -o libheif.tar.gz && \
    tar -xzvf libheif.tar.gz && cd libheif-${LIB_HEIF_VERSION}/ && ./autogen.sh && ./configure && make && make install && cd .. && \
    ldconfig /usr/local/lib && \
    rm -rf libheif-${LIB_HEIF_VERSION} && rm libheif.tar.gz && \
    # Building ImageMagick
    git clone https://github.com/ImageMagick/ImageMagick.git && \
    cd ImageMagick && git checkout ${IM_VERSION} && \
    ./configure --without-magick-plus-plus --disable-docs --disable-static --with-tiff && \
    make && make install && \
    ldconfig /usr/local/lib && \
    apt-get remove --autoremove --purge -y gcc make cmake curl g++ yasm git autoconf pkg-config libpng-dev libjpeg62-turbo-dev libde265-dev libx265-dev libxml2-dev libtiff-dev libfontconfig1-dev libfreetype6-dev && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /ImageMagick

    # Update and install depedencies
RUN apt-get update && \
    apt-get install -y wget unzip bc libleptonica-dev

# Packages to complie Tesseract
RUN apt-get install -y --reinstall make && \
    apt-get install -y g++ autoconf automake libtool pkg-config \
     libpng-dev libjpeg62-turbo-dev libtiff5-dev libicu-dev \
     libpango1.0-dev autoconf-archive ffmpeg libsm6 libxext6


#RUN apt-get install -y poppler-utils
# Set working directory
WORKDIR /app

RUN mkdir src && cd /app/src && \
    wget https://github.com/tesseract-ocr/tesseract/archive/refs/tags/5.0.1.zip && \
	unzip 5.0.1.zip && \
    cd /app/src/tesseract-5.0.1 && ./autogen.sh && ./configure && make && make install && ldconfig && \
    make training && make training-install
RUN cd /usr/local/share/tessdata && wget https://github.com/tesseract-ocr/tessdata_fast/blob/main/eng.traineddata?raw=true -O eng.traineddata \
    && wget https://github.com/tesseract-ocr/tessdata_fast/blob/main/ron.traineddata?raw=true -O ron.traineddata && \
    apt-get remove --autoremove --purge -y wget unzip make g++ autoconf automake libtool pkg-config \
     libpng-dev libjpeg62-turbo-dev libtiff5-dev libicu-dev \
     libpango1.0-dev autoconf-archive

# Setting the data prefix
ENV TESSDATA_PREFIX=/usr/local/share/tessdata

FROM env-setup as test
ENV PYTHONUNBUFFERED 1
RUN useradd --create-home --shell /bin/bash app_user
WORKDIR /home/app_user
USER app_user
COPY . .
RUN python -m pip install -r requirements.txt
RUN python -m pytest -n 6

FROM env-setup as install
ENV PYTHONUNBUFFERED 1
RUN useradd --create-home --shell /bin/bash app_user
WORKDIR /home/app_user
USER app_user
COPY --chown=app_user . .
RUN pip install .
ENV PATH /home/app_user/.local/bin:$PATH
RUN rm -r test_examples && rm -r tests
ENTRYPOINT ["./entrypoint.sh"]
CMD ["insurance-db"]


#      docker build --target test -t insurance-db:test .
#      docker build -t insurance-db:0.0.2.
