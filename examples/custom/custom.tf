# mandatory variables calculated by the tool
variable "net_octet" {
}

variable "basename" {
}

# mandatory custom variables given to the CLI using --tfvar
variable "image1" {
}

variable "image2" {
}

provider "libvirt" {
     uri = "qemu:///system"
}

resource "libvirt_volume" "myvdisk" {
  name = "qatrfm-vdisk-${var.basename}-${count.index}.qcow2"
  pool = "default"
  count = 2
  source = "${count.index == 0 ? var.image1 : var.image2}"
  format = "qcow2"
}


resource "libvirt_network" "my_net1" {
   name = "qatrfm-net-${var.basename}-1"
   addresses = ["10.${var.net_octet}.10.0/24"]
   dhcp {
        enabled = true
   }
   bridge="qatrfm-br-1"
}

resource "libvirt_network" "my_net2" {
   name = "qatrfm-net-${var.basename}-2"
   addresses = ["10.${var.net_octet}.20.0/24"]
   dhcp {
        enabled = true
   }
   bridge="qatrfm-br-2"
}

resource "libvirt_domain" "domain-sle" {
  name = "qatrfm-vm-${var.basename}-${count.index}"
  memory = "2048"
  vcpu = 2
  count = 2

  network_interface {
    network_id = "${libvirt_network.my_net1.id}"
    wait_for_lease = true
  }

  network_interface {
    network_id = "${libvirt_network.my_net2.id}"
    wait_for_lease = true
  }

  disk {
   volume_id = "${libvirt_volume.myvdisk.*.id[count.index]}"
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
