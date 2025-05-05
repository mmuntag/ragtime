FROM nvidia/cuda:12.3.0-runtime-ubuntu22.04

# Install system packages (excluding python3 and pip)
RUN DEBIAN_FRONTEND=noninteractive apt-get update -qq && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -qy \
    sudo vim nano git curl wget mc less gcc g++ make build-essential \
    libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev \
    openssh-server ffmpeg libsm6 libxext6 ca-certificates bzip2 && \
    apt-get clean -qq && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    $CONDA_DIR/bin/conda clean -afy

# Set PATH to use conda
ENV PATH=$CONDA_DIR/bin:$PATH

# (Optional) Update conda and create a fresh env
RUN conda update -n base -c defaults conda

# Add gcc
RUN conda install -y gcc_linux-64 gxx_linux-64
ENV CC=gcc CXX=g++

# Use a writable working directory
WORKDIR /workspace

# Set MPL config dir to avoid permission issues
RUN mkdir -m 777 /mplconf
ENV MPLCONFIGDIR=/mplconf

# Allow sudo for docker group
RUN echo "%docker  ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers.d/inside_sudoers

# Copy entrypoint script
COPY entry.sh /entry.sh
RUN chmod +x /entry.sh
ENTRYPOINT ["/entry.sh"]

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu123 && \
    pip install -r /tmp/requirements.txt

RUN conda install python=3.10 numpy pandas pandoc -c conda-forge -y
RUN cd ../
RUN git clone https://github.com/botondbarta/HunSum.git
RUN cd HunSum
RUN pip install -e HunSum

RUN git clone https://github.com/DavidNemeskey/cc_corpus.git
ENV CFLAGS="-Wno-narrowing"
RUN pip install -e cc_corpus
