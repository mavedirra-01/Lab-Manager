from flask import Flask, render_template, request, redirect, url_for
from flask_sockets import Sockets
import subprocess
import random
import time


class Container:
    def __init__(self, name, image):
        self.name = name
        self.status = self.get_status()
        self.image = image

    def get_status(self):
        cmd = f"docker ps --format '{{{{.Status}}}}' -f name={self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            if 'Exited' in output.decode():
                return "Exited"
            else:
                return "Running"
        except subprocess.CalledProcessError:
            return "Not started"

    def start(self):
        cmd = f"docker run -d --rm --hostname {self.name} --name {self.name} {self.image}"
        subprocess.run(cmd.split())

    def stop(self):
        cmd = f"docker stop {self.name}"
        subprocess.run(cmd.split())

    def reset(self):
        self.stop()
        time.sleep(2)
        self.start()


# Get a list of all containers
output = subprocess.check_output(
    'docker ps -a --format "{{.Names}} {{.Image}}"', shell=True)
output = output.decode().strip()
if output:
    container_list = output.split('\n')
else:
    container_list = []

# Create instances of the Container class for each container
containers = {}
for container_info in container_list:
    name, image = container_info.split()
    containers[name] = Container(name, image)



app = Flask(__name__)


containers = {
    'nginx': Container('nginx', 'nginx:latest'),
}

# Define routes for starting, stopping, and resetting containers
@app.route('/start_container/<container_name>', methods=['POST'])
def start_container(container_name):
    if container_name in containers:
        containers[container_name].start()
    return redirect(url_for('index'))


@app.route('/stop_container/<container_name>', methods=['POST'])
def stop_container(container_name):
    if container_name in containers:
        containers[container_name].stop()
    time.sleep(0.5)
    return redirect(url_for('index'))


@app.route('/reset_container/<container_name>', methods=['POST'])
def reset_container(container_name):
    if container_name in containers:
        containers[container_name].reset()
    return redirect(url_for('index'))


@app.route('/terminal/<container_name>/', methods=['POST'])
def terminal(container_name):
    port = random.randint(10001, 65535)
    ttyd_command = f"ttyd -p {port} docker exec -it {container_name} /bin/bash"
    subprocess.Popen(ttyd_command.split())
    time.sleep(1)
    return redirect(f"http://192.168.2.136:{port}")


@app.route('/')
def index():
    containers_status = {}
    for name, container in containers.items():
        containers_status[name] = {
            'status': container.get_status()
        }
    return render_template('index.html', containers=containers_status, containers_list=containers)

    


# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
