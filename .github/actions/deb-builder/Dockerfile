FROM debian:stable-slim
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends --option Dpkg::Use-Pty=0 build-essential debhelper && rm -r /var/cache/debconf/*-old /var/lib/dpkg/*-old /var/lib/apt/lists/*
COPY entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
