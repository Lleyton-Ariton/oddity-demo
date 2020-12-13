FROM python:3.6
FROM rust:slim-buster

RUN apt-get -y update
RUN apt-get install -y sudo

RUN adduser --disabled-password --gecos '' admin
RUN adduser admin sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers
RUN chown -R admin /home/admin

USER admin

RUN sudo apt-get install -y python3 make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git && \
    curl https://pyenv.run | bash && \
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3

ENV HOME /home/admin
ENV PYENV_ROOT $HOME/.pyenv
ENV POETRY_ROOT $HOME/.poetry
ENV CARGO_ROOT /usr/local/cargo
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
ENV PATH $POETRY_ROOT/bin:$PATH
ENV PATH $CARGO_ROOT/bin:$PATH

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

CMD set -eux; \
    \
    url="https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init"; \
    wget "$url"; \
    chmod +x rustup-init; \
    ./rustup-init -y --no-modify-path --default-toolchain nightly; \
    rm rustup-init; \
    chmod -R a+w $RUSTUP_HOME $CARGO_HOME; \
    rustup --version; \
    cargo --version; \
    rustc --version;

WORKDIR /app
ADD . /app

RUN sudo apt-get install python3-pip -y
RUN sudo apt-get install python3-venv -y

RUN sudo python3 -m venv venv
CMD sudo source bin/activate

RUN sudo pip3 install streamlit
RUN sudo pip3 install setuptools-rust
WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

EXPOSE 8501

CMD streamlit run ./app/app.py
