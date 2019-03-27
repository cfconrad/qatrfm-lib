variable "image" {
}

provider "libvirt" {
     uri = "qemu:///system"
}

resource "libvirt_volume" "myvdisk" {
  name = "qatrfm-vdisk.qcow2"
  pool = "default"
  source = "${var.image}"
  format = "qcow2"
}


resource "libvirt_network" "my_net1" {
   name = "qatrfm-net"
   addresses = ["10.42.10.0/24"]
   dhcp {
        enabled = true
   }
   bridge="qatrfm-br-1"
}

resource "libvirt_domain" "domain-sle" {
  name = "qatrfm-vm"
  memory = "2048"
  vcpu = 2
  network_interface {
    network_id = "${libvirt_network.my_net1.id}"
    wait_for_lease = true
  }

  disk {
   volume_id = "${libvirt_volume.myvdisk.id}"
  }

  console {
    type        = "pty"
    target_port = "0"
    target_type = "serial"
  }

  console {
      type        = "pty"
      target_type = "virtio"
      target_port = "1"
  }

  graphics {
    type = "vnc"
    listen_type = "address"
    autoport = "true"
  }
}

output "domain_ips" {
    value = "${libvirt_domain.domain-sle.*.network_interface.0.addresses}"
}

output "domain_names" {
    value = "${libvirt_domain.domain-sle.*.name}"
}
