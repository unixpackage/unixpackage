FROM ubuntu:14.04

RUN apt-get update && apt-get install -y firefox

# Replace 1000 with your user / group id
RUN export uid=1000 gid=1000 && \
    mkdir -p /home/hitch && \
    echo "hitch:x:${uid}:${gid}:Developer,,,:/home/hitch:/bin/bash" >> /etc/passwd && \
    echo "hitch:x:${uid}:" >> /etc/group && \
    echo "hitch ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/hitch && \
    chmod 0440 /etc/sudoers.d/hitch && \
    chown ${uid}:${gid} -R /home/hitch

USER hitch
ENV HOME /home/hitch
CMD /usr/bin/firefox

#docker run -ti --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix firefox
