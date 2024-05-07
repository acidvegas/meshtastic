# Meshtastic MQTT
> Work in progress still, come back later...

###### default.conf
```
# Insecure
listener 1883

# TLS/SSL
listener 8883
acl_file /etc/mosquitto/conf.d/aclfile
protocol mqtt
require_certificate false
certfile /etc/mosquitto/certs/cert.pem
cafile /etc/mosquitto/certs/fullchain.pem
keyfile /etc/mosquitto/certs/privkey.pem

listener 8083
protocol websockets
certfile /etc/mosquitto/certs/cert.pem
cafile /etc/mosquitto/certs/fullchain.pem
keyfile /etc/mosquitto/certs/privkey.pem
```

###### /etc/mosquitto/conf.d/aclfile
```
user acidvegas
topic readwrite msh/#

user mate
topic readwrite msh/#

pattern write $SYS/broker/connection/%c/state
```

###### mosquito.conf
```
pid_file /run/mosquitto/mosquitto.pid

per_listener_settings true
allow_anonymous false
persistence true
persistence_location /var/lib/mosquitto
password_file /etc/mosquitto/passwd

log_dest file /var/log/mosquitto/mosquitto.log

include_dir /etc/mosquitto/conf.d
```