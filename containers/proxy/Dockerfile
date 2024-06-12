# Use the official HAProxy image from the Docker Hub
FROM haproxy:latest

# Copy the entrypoint script to the container
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg 

# Set execute permissions for the entrypoint script
#RUN chmod 777 entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["haproxy", "-f", "/usr/local/etc/haproxy/haproxy.cfg"]

# Expose the port (will be defined by environment variable)
EXPOSE ${LOCAL_PORT}
