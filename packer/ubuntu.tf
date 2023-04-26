terraform {
  required_providers {
    libvirt = {
      source = "dmacvicar/libvirt"
    }
  }
}

provider "libvirt" {
  uri = "qemu:///system"
}

resource "libvirt_volume" "ubuntu_disk" {
  name        = "ubuntu.qcow2"
  pool        = "default"
  source_file = "/ubuntu-kvm-0.qcow2"
  format      = "qcow2"
  size        = "${var.disk_size}"
}

resource "libvirt_domain" "ubuntu_vm" {
  name   = "ubuntu-vm"
  memory = 2048
  vcpu   = 2

  disk {
    volume_id = libvirt_volume.ubuntu_disk.id
  }

  network_interface {
    network_name = "default"
  }

  console {
    type        = "pty"
    target_type = "serial"
    target_port = "0"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "1"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "2"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "3"
  }

  console {
    type        = "pty"
    target_type = "virtio"
    target_port = "4"
  }
}

output "ip_address" {
  value = libvirt_domain.ubuntu_vm.ip_address
}

