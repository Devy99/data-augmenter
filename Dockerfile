FROM openjdk:17.0.1-jdk-slim

RUN apt-get update && \
    apt-get install --no-install-recommends -y software-properties-common && \
    apt-get install --no-install-recommends -y python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /data-augmenter

COPY requirements.txt ./
RUN pip --no-cache-dir install -r requirements.txt

COPY . .

RUN chmod +x ./data_augmenter.py
ENTRYPOINT ["python3", "./data_augmenter.py"]