FROM python:3.8
WORKDIR /app
VOLUME /scan_input
VOLUME /digital_depot
VOLUME /pictures
VOLUME /config
VOLUME /tmp
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY handle_documents.py handle_documents.py
COPY doc_mgnt_libs doc_mgnt_libs
CMD ["python3", "/app/handle_documents.py", "/config"]
