from flask import Flask, render_template, request
import docker
client = docker.from_env()


app = Flask(__name__)

@app.route('/start', methods=['POST'])
def start_container():
    container_id = request.form['id']
    container = client.containers.get(container_id)
    container.start()
    return 'Container started'


@app.route('/stop', methods=['POST'])
def stop_container():
    container_id = request.form['id']
    container = client.containers.get(container_id)
    container.stop()
    return 'Container stopped'



@app.route('/')
def index():
    containers = client.containers.list()
    return render_template('index2.html', containers=containers)


# Define a class for managing VMs
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
