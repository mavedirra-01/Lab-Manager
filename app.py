# class ContainerManager:
#     def __init__(self):
#         self.containers = {}


#     def update_containers(self):
#         cmd = "docker ps -a --format '{{.Names}} {{.Image}} {{.Status}}' | awk '{print $1, $2, $3}'"
#         output = subprocess.check_output(cmd, shell=True).decode('utf-8')
#         for line in output.splitlines():
#             name, image, status = line.split()
#             # if name not in self.containers:
#             self.containers[name] = Container(name, image)
#         if 'Exited' in output.decode():
#             return "Exited"
#         if not output.decode():
#             return "Not Started"
#         else:
#             return "Running"
#             # else:
#             #     self.containers[name].image = image


#     def update_containers_thread(self):
#         self.update_containers()

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sockets import Sockets
import subprocess
import random
from threading import Thread
import time




class Container:
    def __init__(self, name, image):
        self.name = name
        self.status = self.get_status()
        self.image = image

    def get_status(self):
        cmd = f"docker ps -a --format '{{{{.Status}}}}' -f name={self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            if 'Exited' in output.decode():
                return "Exited"
            if not output.decode():
                return "Not Started"
            else:
                return "Running"
        except subprocess.CalledProcessError:
            return "Not started"

    def start(self):
        cmd = f"docker run -d --hostname {self.name} --name {self.name} {self.image}"
        cmd_failed = f"docker start {self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            subprocess.run(cmd.split())
            if 'Conflict' in output.decode():
                subprocess.run(cmd_failed.split())
        except subprocess.CalledProcessError:
            pass

    def remove(self):
        cmd = f"docker rm {self.name}"
        subprocess.run(cmd.split())

    def stop(self):
        cmd = f"docker stop {self.name}"
        subprocess.run(cmd.split())

    def reset(self):
        self.stop()
        time.sleep(2)
        self.start()
    
    def get_containers(self):
        output = subprocess.check_output(
            ['docker', 'ps', '-a', '--format', '{{.Names}} {{.Image}} {{.Status}}'])
        lines = output.decode('utf-8').strip().split('\n')
        containers = []
        for line in lines[1:]:
            name, image, status = line.split()
            containers.append({
                'name': name,
                'image': image,
                'status': status
            })
        return containers


app = Flask(__name__)

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
def containers_status():
    output = subprocess.check_output(
        'docker ps -a --format "{{.Names}} {{.Image}} {{.Status}}" | awk \'{print $1, $2, $3}\'', shell=True, text=True)
    lines = output.strip().split('\n')
    containers_list = []
    for line in lines[1:]:
        name, image, status = line.split()
        container = {
            'name': name,
            'image': image,
            'status': status
        }
        containers_list.append(container)
    return jsonify(containers_list)




@app.route('/')
def index():
    containers_status = {}
    for name, container in containers():
        containers_status[name] = {
            'status': container.status
        }
    return render_template('index.html', containers=containers_status, containers_list=containers)



# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
