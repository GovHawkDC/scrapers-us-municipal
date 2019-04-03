FROM        ubuntu:artful
MAINTAINER  Tim Showers <tim.showers@govhawk.com>

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python2.7 \
    python-pip \
    python-lxml \
    libssl-dev \
    mdbtools \
    python-dev \
    python3-dev \
    poppler-utils \
    python-virtualenv \
    python3.5 \
    python3-lxml \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    gdal-bin \
    s3cmd \
    freetds-dev \
    curl \
    wget \
    unzip \
    gnupg \
    dirmngr

RUN mkdir -p /opt/sunlightfoundation.com/

RUN virtualenv -p $(which python3) /opt/sunlightfoundation.com/venv-pupa/
RUN /opt/sunlightfoundation.com/venv-pupa/bin/pip install -e git+https://github.com/opencivicdata/python-opencivicdata.git#egg=python-opencivicdata

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'en_US.UTF-8'
ENV LANGUAGE=en_US:en
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PUPA_ENV /opt/sunlightfoundation.com/venv-pupa/

ADD . /opt/sunlightfoundation.com/scrapers-us-municipal/

RUN /opt/sunlightfoundation.com/venv-pupa/bin/pip install lxml
RUN /opt/sunlightfoundation.com/venv-pupa/bin/pip install -r /opt/sunlightfoundation.com/scrapers-us-municipal/requirements.txt
RUN /opt/sunlightfoundation.com/venv-pupa/bin/pip install -e git+https://github.com/GovHawkDC/pupa.git@feature/custom-outputs#egg=pupa

RUN echo "/opt/sunlightfoundation.com/scrapers-us-municipal/" > /usr/lib/python3/dist-packages/scrapers-us-municipal.pth

# Adding these so we can git pull in pupa-scrape.sh...
RUN git config --global user.email "user@example.org"
RUN git config --global user.name "Example User"
RUN git config --global core.mergeoptions --no-edit

WORKDIR /opt/sunlightfoundation.com/scrapers-us-municipal/
RUN git remote set-url origin https://github.com/GovHawkDC/scrapers-us-municipal.git
ENTRYPOINT ["/opt/sunlightfoundation.com/scrapers-us-municipal/pupa-scrape.sh"]