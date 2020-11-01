FROM debian:stable 
LABEL maintainer "matt salmon <matt_salmon@hotmail.com>"

## For geckodriver installation: curl/wget/libgconf/unzip
RUN apt-get update -y && apt-get install -y wget curl unzip libgconf-2-4 nano
## For project usage: python3/python3-pip/chromium
## Installing Firefox to Debian Stretch https://unix.stackexchange.com/a/406554/169768
RUN sh -c 'echo "APT::Default-Release "stable";" >> /etc/apt/apt.conf' 
RUN sh -c 'echo "deb http://ftp.hr.debian.org/debian sid main contrib non-free" >> /etc/apt/sources.list'
#RUN apt-get update -y && apt-get install -yt sid firefox
RUN apt-get update -y && apt-get install -y python3 python3-pip 


# Download, unzip, and install geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'`/geckodriver-`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'`-linux64.tar.gz
RUN tar -zxf geckodriver-`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'`-linux64.tar.gz -C /usr/local/bin
RUN chmod +x /usr/local/bin/geckodriver

# Set display port as an environment variable
ENV DISPLAY=:99

# Create directory for project name (ensure it does not conflict with default debian /opt/ directories).
#RUN mkdir -p /opt/app
#WORKDIR /opt/app
WORKDIR /usr/src

# Add working directory to the python path
ENV PYTHONPATH "${PYTONPATH}:/usr/src"

## Your python project dependencies
#RUN pip3 install selenium
## or install from dependencies.txt, comment above and uncomment below
COPY requirements.txt .
RUN pip3 install -r requirements.txt

## If VOLUME not used in docker-compose.yml
## Copy over project/script (feel free to combine these if your project is a combination of both directories and top-level files)
### For projects which are modules
#COPY . .
## For projects which are single scripts
#COPY test.py .


# Bash script to invoke project
#COPY run.sh .
CMD ["python3", "tests/webdriver_test.py"]





