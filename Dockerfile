# set base image (host OS)
FROM python:3.8

# copy the dependencies file to the working directory
ADD ./* $HOME/src/

RUN ls
# install dependencies
RUN pip install -r build/requirements.txt

RUN ls
RUN pwd

# command to run on container start
CMD [ "python3", "start.py" ]