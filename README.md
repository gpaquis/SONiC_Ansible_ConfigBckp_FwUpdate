# Backup Config and Deploy Firmware on Dell Enterprise SONiC with Ansible

Built and maintained by [Gerald PAQUIS](https://github.com/gpaquis) 

--------------------
This Repo contains an Ansible playbook script backup the config file on a remote server with SCP and/or deploy a new Firmware Release

## Contents

- [Description and Objective](#-description-and-objective)
- [Requirements](#-requirements)
- [Usage and Configuration](#-Usage-and-Configuration)


## 🚀 Description and Objective

The Ansible playbook, backup config file and deploy a new firmware. <br />
This script is for purpose test only and explain howto use DES and CLI collection

## 📋 Requirements
- Ansible
- SSH server with SCP allow to store the config file


## 🏁 Usage and Configuration
Run the playbook with the ansible-playbook command  <br />
For Backup Config file on a remote switch available in the inventory <br />
   ansible-playbook -vvv -i inventory.yaml sonic_backup_config.yaml
