from flask import Flask, render_template, request, redirect, url_for
from flask_sockets import Sockets
import subprocess
import random
# from guacamole.client import GuacamoleClient
# from guacamole.protocol import GuacamoleProtocol

# class VM:
#     def __init__(self, name, image):
#         self.name = name
#         self.image = image
#         self.state = self.get_state()

#     def get_state(self):
#         cmd = f"virsh list --all | grep {self.name} | awk '{{print $3}}'"
#         output = subprocess.check_output(cmd, shell=True)
#         return output.decode('utf-8').strip()

#     def start(self):
#         cmd = f"virsh start {self.name}"
#         subprocess.run(cmd.split())

#     def stop(self):
#         cmd = f"virsh shutdown {self.name}"
#         subprocess.run(cmd.split())

#     def reset(self):
#         self.stop()
#         cmd = f"virsh snapshot-revert {self.name} --current"
#         subprocess.run(cmd.split())
#         self.start()

# class Guacamole:
#     def __init__():
#         @app.route('/connect_to_terminal')
#         def connect_to_terminal():
#             # Connect to the Guacamole server
#             guac_client = GuacamoleClient('localhost', 8080, 'osi', 'osi')

#             # Create a new Guacamole connection for the terminal
#             connection = guac_client.create_connection(protocol=GuacamoleProtocol.RDP)
#             connection.parameters['hostname'] = 'localhost'
#             connection.parameters['port'] = '22'
#             connection.parameters['password'] = 'osi'

#             # Start the Guacamole session and get the session URL
#             session_url = guac_client.get_session_url(connection)

#             # Return the session URL to the client
#             return session_url


#         @app.route('/connect_to_spice')
#         def connect_to_spice():
#             # Connect to the Guacamole server
#             guac_client = GuacamoleClient('localhost', 8080, 'osi', 'osi')

#             # Create a new Guacamole connection for the Spice
#             connection = guac_client.create_connection(
#                 protocol=GuacamoleProtocol.SPICE)
#             connection.parameters['hostname'] = 'localhost'
#             connection.parameters['port'] = '5900'
#             connection.parameters['password'] = 'spicepassword'

#             # Start the Guacamole session and get the session URL
#             session_url = guac_client.get_session_url(connection)

#             # Return the session URL to the client
#             return session_url


class Container:
    def __init__(self, name, image):
        self.name = name
        self.status = self.get_status()
        self.image = image

    def get_status(self):
        cmd = f"docker ps --format '{{{{.Names}}}}' | grep {self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            return "Running"
        except subprocess.CalledProcessError:
            return "Not started"

    def start(self):
        cmd = f"docker run -d --rm --name {self.name} {self.image}"
        subprocess.run(cmd.split())

    def stop(self):
        cmd = f"docker stop {self.name}"
        subprocess.run(cmd.split())

    def reset(self):
        self.stop()
        cmd = f"docker rm {self.name}"
        subprocess.run(cmd.split())
        self.start()


app = Flask(__name__)




# vms = {
#     'Ubuntu 20.04': VM('ubuntu20', 'ubuntu20.qcow2'),
# }

containers = {
    'nginx': Container('nginx', 'nginx:latest'),
}

# Define routes for starting, stopping, and resetting VMs




# @app.route('/start_vm/<vm_name>', methods=['POST'])
# def start_vm(vm_name):
#     if vm_name in vms:
#         vms[vm_name].start()
#     return redirect(url_for('index'))


# @app.route('/stop_vm/<vm_name>', methods=['POST'])
# def stop_vm(vm_name):
#     if vm_name in vms:
#         vms[vm_name].stop()
#     return redirect(url_for('index'))


# @app.route('/reset_vm/<vm_name>', methods=['POST'])
# def reset_vm(vm_name):
#     if vm_name in vms:
#         vms[vm_name].reset()
#     return redirect(url_for('index'))


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
    return redirect(url_for('index'))


@app.route('/reset_container/<container_name>', methods=['POST'])
def reset_container(container_name):
    if container_name in containers:
        containers[container_name].reset()
    return redirect(url_for('index'))


@app.route('/terminal/<container_name>')
def terminal(container_name):
    port = random.randint(10001, 65535)
    ttyd_command = f"ttyd -p {port} docker exec -it /bin/bash {container_name}"
    subprocess.Popen(ttyd_command.split())
    return render_template('index.html', container_name=container_name, port=port)

# Define route for displaying the main page
@app.route('/')
def index():
    # vms_status = {}
    # for name, vm in vms.items():
    #     vms_status[name] = {
    #         'state': vm.get_state()
    #     }
    containers_status = {}
    for name, container in containers.items():
        containers_status[name] = {
            'status': container.get_status()
        }
    return render_template('index.html', containers=containers_status, port=port)
    


# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
