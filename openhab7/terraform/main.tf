# Optional: Terraform - e.g. cloud resources for hosting the stack
# This is a minimal placeholder; extend with provider (AWS/GCP/Azure) and compute/network.

terraform {
  required_version = ">= 1.0"
  # backend "remote" { }
}

# Example: local Docker provider (requires kreuzwerker/docker)
# Uncomment and run terraform init + apply if you use Terraform for Docker.

# variable "openhab_image" {
#   default = "openhab/openhab:4.2"
# }
#
# resource "docker_network" "openhab_net" {
#   name = "openhab7-net"
# }
#
# output "network_name" {
#   value = docker_network.openhab_net.name
# }
