FROM elasticsearch:6.5.4

WORKDIR /usr/share/elasticsearch

RUN wget https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v6.5.4/elasticsearch-analysis-ik-6.5.4.zip
RUN mkdir -p plugins/ik/ && \
    unzip elasticsearch-analysis-ik-6.5.4.zip -d plugins/ik/ && \
    rm -f elasticsearch-analysis-ik-6.5.4.zip

RUN chown -R elasticsearch:elasticsearch plugins/ik