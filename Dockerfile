FROM debian:buster-slim

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH

RUN apt-get update --fix-missing && \
    apt-get install -y wget bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 git mercurial subversion && \
        apt-get clean

        RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
            /bin/bash ~/miniconda.sh -b -p /opt/conda && \
                rm ~/miniconda.sh && \
                    /opt/conda/bin/conda clean -tipsy && \
                        ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
                            echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
                                echo "conda activate base" >> ~/.bashrc && \
                                    find /opt/conda/ -follow -type f -name '*.a' -delete && \
                                        find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
                                            /opt/conda/bin/conda clean -afy

RUN mkdir ScienceDynamics
COPY ./*  ScienceDynamics/

RUN which python
RUN conda install --yes pip
RUN which pip
RUN pip install -r ScienceDynamics/requirements.txt
RUN pip list
RUN apt-get install -y  gcc
RUN apt-get install -y g++
RUN pip install pycld2
RUN conda install --yes pycurl
RUN pip install wptools 
RUN pip install notebook

RUN mkdir /root/.scidyn2
RUN mkdir ScienceDynamics/examples/Coronavirus/Data
RUN pip install jupyterlab
EXPOSE 8888

CMD ["jupyter", "lab", "--port=8888", "--no-browser", "--ip=0.0.0.0", "--allow-root"]
