FROM jupyter/datascience-notebook

USER $NB_UID
RUN conda install --quiet --yes \
    'scikit-learn=1.2.2' \
    'boto3' \
    'pytest' && \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

WORKDIR ${HOME}