# Apache MADlib has no official prebuilt image, so build it from source
# on top of the official PostgreSQL image.
# Pinned to bookworm: its PL/Python is Python 3.11, which still ships distutils
# (MADlib's Python code requires it; Python 3.12 removed it entirely).
FROM postgres:15-bookworm

ARG MADLIB_VERSION=2.1.0

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake m4 flex bison \
        python3 python3-distutils wget ca-certificates \
        postgresql-server-dev-15 libpq-dev \
        postgresql-plpython3-15 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp
# NOTE: build serially (no -j) - MADlib's bundled boost ExternalProject races
# under parallel make and fails.
RUN wget -q "https://downloads.apache.org/madlib/${MADLIB_VERSION}/apache-madlib-${MADLIB_VERSION}-src.tar.gz" \
    && tar xzf "apache-madlib-${MADLIB_VERSION}-src.tar.gz" \
    && mkdir "apache-madlib-${MADLIB_VERSION}-src/build" \
    && cd "apache-madlib-${MADLIB_VERSION}-src/build" \
    && cmake .. \
    && make \
    && make install \
    && rm -rf /tmp/apache-madlib-*

# MADlib needs a live TCP connection to register itself, which is only available
# after the server has fully started (not during initdb). A wrapper entrypoint
# installs the 'madlib' schema once in the background, then hands off to postgres.
COPY entrypoint-madlib.sh /usr/local/bin/entrypoint-madlib.sh
RUN chmod +x /usr/local/bin/entrypoint-madlib.sh
ENTRYPOINT ["/usr/local/bin/entrypoint-madlib.sh"]
CMD ["postgres"]
