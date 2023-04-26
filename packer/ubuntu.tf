provider "libvirt" {
  uri = "qemu:///system"
}

resource "libvirt_volume" "ubuntu" {
  name = "ubuntu.qcow2"
  size = "10G"
}

resource "libvirt_domain" "ubuntu" {
  name   = "ubuntu"
  memory = "1024"
  vcpu   = 1

  disk {
    volume_id = libvirt_volume.ubuntu.id
  }

  network_interface {
    network_name = "default"
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  graphics {
    type        = "spice"
    autoport    = "yes"
  }

  user_data = "${file("${path.module}/cloud-config.yaml")}"
}
