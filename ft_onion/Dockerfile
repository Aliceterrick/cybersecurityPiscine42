FROM ubuntu:22.04


RUN apt-get update && apt-get install -y curl ca-certificates gnupg
RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /usr/share/keyrings/nodesource.gpg
RUN echo "deb [signed-by=/usr/share/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

RUN apt-get update && apt-get install -y \
    nginx \
    tor \
    openssh-server \
    openssl \
    nodejs \
    postgresql-client \
    build-essential \
    python3-minimal \
    && rm -rf /var/lib/apt/lists/*
    
RUN curl -o /usr/local/bin/gosu -SL "https://github.com/tianon/gosu/releases/download/1.16/gosu-$(dpkg --print-architecture)" \
    && chmod +x /usr/local/bin/gosu 
    
    
RUN useradd -r -u 1000 -d /var/lib/tor -s /bin/false toruser
RUN mkdir -p /var/lib/tor/hidden_service && \
    chown -R toruser:toruser /var/lib/tor && \
    chmod 700 /var/lib/tor/hidden_service
    
RUN mkdir /run/sshd && \
    ssh-keygen -A && \
    rm /etc/ssh/sshd_config

RUN mkdir -p /app
WORKDIR /app
    
RUN chown -R www-data:www-data /app \
    && chmod -R 755 /app \
    && mkdir -p /var/log/nginx \
    && touch /var/log/nginx/access.log /var/log/nginx/error.log \
    && chown -R www-data:www-data /var/log/nginx    

COPY /app/package*.json ./

RUN npm install

COPY /tor/torrc /etc/tor/torrc
COPY /ssh/sshd_config /etc/ssh/sshd_config
COPY nginx.conf /etc/nginx/nginx.conf
COPY /app /app

RUN npm install -g pm2

EXPOSE 80 4242

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]

