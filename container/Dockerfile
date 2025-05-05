FROM nvidia/cuda:12.3.0-runtime-ubuntu22.04

# Install some basic apt packages
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq &&     DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -qy     sudo vim nano git curl wget mc less python3-pip     openssh-server     ffmpeg libsm6 libxext6  &&     apt-get clean -qq &&     rm -rf /var/lib/apt/lists/* &&     rm -rf /tmp/*

WORKDIR /workspace

RUN mkdir -m 777 /mplconf
ENV MPLCONFIGDIR=/mplconf
RUN echo "%docker  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/inside_sudoers

COPY entry.sh /entry.sh
RUN chmod +x /entry.sh
ENTRYPOINT ["/entry.sh"]

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install --upgrade pip
RUN pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu123
RUN pip3 install -r /tmp/requirements.txt
