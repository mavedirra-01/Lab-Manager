from flask import Flask, render_template, request, redirect, url_for
import subprocess


class VM:
    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.id = self.get_id()
        self.state = self.get_state()

    def get_id(self):
        cmd = f"virsh list --all | grep {self.name} | awk '{{print $1}}'"
        output = subprocess.check_output(cmd, shell=True)
        return output.decode('utf-8').strip()

    def get_state(self):
        cmd = f"virsh list --all | grep {self.name} | awk '{{print $3}}'"
        output = subprocess.check_output(cmd, shell=True)
        return output.decode('utf-8').strip()

    def start(self):
        cmd = f"virsh start {self.name}"
        subprocess.run(cmd.split())

    def stop(self):
        cmd = f"virsh shutdown {self.name}"
        subprocess.run(cmd.split())

    def reset(self):
        self.stop()
        cmd = f"virsh snapshot-revert {self.name} --current"
        subprocess.run(cmd.split())
        self.start()


class Container:
    def __init__(self, name, image):
        self.name = name
        self.id = self.get_id()
        self.status = self.get_status()
        self.image = image

    def get_id(self):
        cmd = f"docker ps -aqf name={self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            return output.decode('utf-8').strip()
        except subprocess.CalledProcessError:
            return "N/A"

    def get_status(self):
        cmd = f"docker ps --format '{{{{.Names}}}}' | grep {self.name}"
        try:
            output = subprocess.check_output(cmd, shell=True)
            if output.decode('utf-8').strip() == "":
                print(output)
                return "not started"
            else:
                return "not started"
        except subprocess.CalledProcessError:
            return False

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

vms = {
    'Ubuntu 20.04': VM('ubuntu20', 'ubuntu20.qcow2'),
}

containers = {
    'Nginx': Container('nginx', 'nginx:latest'),
}

# Define routes for starting, stopping, and resetting VMs


@app.route('/start_vm/<vm_name>', methods=['POST'])
def start_vm(vm_name):
    if vm_name in vms:
        vms[vm_name].start()
    return redirect(url_for('index'))


@app.route('/stop_vm/<vm_name>', methods=['POST'])
def stop_vm(vm_name):
    if vm_name in vms:
        vms[vm_name].stop()
    return redirect(url_for('index'))


@app.route('/reset_vm/<vm_name>', methods=['POST'])
def reset_vm(vm_name):
    if vm_name in vms:
        vms[vm_name].reset()
    return redirect(url_for('index'))


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


# Define route for displaying the main page
@app.route('/')
def index():
    vms_status = {}
    for name, vm in vms.items():
        vms_status[name] = {
            'id': vm.id,
            'state': vm.get_state()
        }
    containers_status = {}
    for name, container in containers.items():
        containers_status[name] = {
            'id': container.id,
            'status': container.get_status()
        }
    return render_template('index.html', vms=vms_status, containers=containers_status)


# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
