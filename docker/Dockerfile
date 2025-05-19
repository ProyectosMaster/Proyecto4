FROM jupyter/pyspark-notebook

# Copia el entorno Conda
COPY env.yml /tmp/env.yml

# Crea el entorno Conda y límpialo después
RUN conda env create -f /tmp/env.yml && \
    conda clean -afy

# Usa el entorno como entorno principal
ENV PATH /opt/conda/envs/recommender-env/bin:$PATH
