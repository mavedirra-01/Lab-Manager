import docker
import time
import random
import json
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)
client = docker.from_env()


class Container:
    def __init__(self, name, image):
        self.name = name
        self.status = self.get_status()
        self.image = image

    def get_status(self):
        try:
            container = client.containers.get(self.name)
            return container.status
        except docker.errors.NotFound:
            return "Not started"

    def start(self):
        try:
            client.containers.run(self.image, detach=True,
                                  hostname=self.name, name=self.name)
        except docker.errors.APIError:
            pass

    def remove(self):
        try:
            container = client.containers.get(self.name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass

    def stop(self):
        try:
            container = client.containers.get(self.name)
            container.stop()
        except docker.errors.NotFound:
            pass

    def reset(self):
        self.stop()
        time.sleep(2)
        self.start()

    def update_containers(self):
        global containers
        containers_status = {}
        for container in client.containers.list(all=True):
            if self.name == container.name:
                self.status = container.status
                break
        if self.name not in containers:
            containers[self.name] = self


containers = {}

for container in client.containers.list(all=True):
    containers[container.name] = Container(
        container.name, container.image.tags[0])


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


@app.route('/containers_status')
def get_containers_status():
    global containers
    containers_status = {}
    for container_name, container in containers.items():
        container.update_containers()
        containers_status[container_name] = container.status
    return json.dumps(containers_status)


@app.route('/')
def index():
    global containers
    for container in client.containers.list(all=True):
        if container.name not in containers:
            containers[container.name] = Container(
                container.name, container.image.tags[0])
    print(containers)
    return render_template('index.html', containers_list=containers)


# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
