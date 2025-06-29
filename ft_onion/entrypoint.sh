#!/bin/bash
set -e


sleep 4

pm2 start /app/server.js --name "web-app" --no-daemon &

sleep 2

nginx -g "daemon off;" &


gosu toruser tor -f /etc/tor/torrc &

while [ ! -f /var/lib/tor/hidden_service/hostname ]; do
    sleep 1
done

echo "=== .ONION ADDRESS ==="
cat /var/lib/tor/hidden_service/hostname


if [ -n "$SSH_USER" ] && [ ! /home/$SSH_USER/.ssh ]; then
    useradd -m -s /bin/bash "$SSH_USER"
    mkdir -p "/home/$SSH_USER/.ssh"
    echo "$SSH_PUBKEY" > "/home/$SSH_USER/.ssh/authorized_keys"
    chown -R "$SSH_USER:$SSH_USER" "/home/$SSH_USER/.ssh"
    chmod 700 "/home/$SSH_USER/.ssh"
    chmod 600 "/home/$SSH_USER/.ssh/authorized_keys"
    echo "$SSH_USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
fi


exec /usr/sbin/sshd -D -e
