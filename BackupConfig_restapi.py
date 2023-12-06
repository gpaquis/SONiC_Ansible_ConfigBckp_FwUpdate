import json
import argparse
import ast
import requests
import configparser
import ipaddress
from requests.exceptions import HTTPError
from requests.auth import HTTPBasicAuth
import base64
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def validate_ip_address(ip_string) -> bool:
    try:
      ip_object = ipaddress.ip_address(ip_string)
      return True
    except ValueError:
      return False

def check_status(remote_sw):
    """
       Check Firmware Status Upgrade
    """

    switch_ip = remote_sw['ip_switch']
    user_name = remote_sw['sonic_username']
    password = remote_sw['sonic_password']

    
    request_data = {
        "openconfig-file-mgmt-private:input": {
           "folder-name": "config:/"
        }
    }

    try:
       response = requests.post(url=f"https://{switch_ip}/restconf/operations/openconfig-file-mgmt-private:dir",
                                data=json.dumps(request_data),
                                headers={'Content-Type': 'application/yang-data+json'},
                                auth=HTTPBasicAuth(f"{user_name}", f"{password}"),
                                verify=False
                                )
       response.raise_for_status()
 
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        #print (response.content)
        return_dict = dict();
        mystatus = json.loads(response.content)
        print(f'{mystatus}')
        #return_dict['myinstall-status'] = mystatus["openconfig-image-management:image-management"]["install"]["state"]["install-status"]
        #return_dict['myimgstatus'] = mystatus["openconfig-image-management:image-management"]["install"]["state"]["transfer-status"]
        #return_dict['percent_install'] = mystatus["openconfig-image-management:image-management"]["install"]["state"]["file-progress"]
        #return_dict['myimage'] = mystatus["openconfig-image-management:image-management"]["global"]["state"]["next-boot"]
        return return_dict


def backup_config(remote_sw,remote_path):
    """
      source:  alway "config://config.db.json"
      destination: method://rem_login:rem_passwd@rem_serv/rem_path/filename+timestamps.json
      copy-config-option: MERGE
    """
    switch_ip = remote_sw['ip_switch']
    user_name = remote_sw['sonic_username']
    password = remote_sw['sonic_password']

    method = remote_path['method']
    rem_serv = remote_path['srv_ip']
    rem_login = remote_path['srv_username']
    rem_passwd = remote_path['srv_passwd']
    rem_path = remote_path['srv_folder']
    filename = {rem_server}+{date}.json

    request_data = {
        "openconfig-file-mgmt-private:input": {
           "source": "config://condig_db.json"
           "destination": method"://"rem_login":"rem_paswd"@"rem_srv""rem_path"/"filename
           "copy-config-option": "MERGE"
        }
    }

    try:
       response = requests.post(url=f"https://{switch_ip}/restconf/operations/openconfig-file-mgmt-private:dir",
                                data=json.dumps(request_data),
                                headers={'Content-Type': 'application/yang-data+json'},
                                auth=HTTPBasicAuth(f"{user_name}", f"{password}"),
                                verify=False
                                )
       response.raise_for_status()
 
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:


def main():
    parser = argparse.ArgumentParser(description='Backup config file tools')
    parser.add_argument("--method", help="ftp or scp", type=str)
    parser.add_argument("--server_ip", help="Remote server IP", type=str)
    parser.add_argument("--switch_ip", help="IP address of the switch", type=str)
    parser.add_argument("--sonic_username", help="SONiC Login", type=str)
    parser.add_argument("--sonic_password", help="SONiC Password", type=str)
    args = parser.parse_args()

    method = args.method.lower()
    filename = args.filename

    ip_switch = args.switch_ip
    server_ip = args.server_ip
    if validate_ip_address(ip_switch) == True and validate_ip_address(server_ip) == True :

     sonic_username = args.sonic_username
     sonic_password = args.sonic_password

     remote_sw = {'ip_switch':ip_switch, 'sonic_username':sonic_username, 'sonic_password':sonic_password}

     if method == "scp" or "ftp":
       return_boot = check_boot_order(remote_sw)
       if return_boot != False:
        boot_current = return_boot['current']
        print(f'current : {boot_current}')

        result = rpcupdate(remote_sw, server_ip=server_ip, method=method, firmware=filename)
        print(f'Start Downloading : {result}')

        return_status = check_status(remote_sw)
        checkstate = return_status['myinstall-status']
        checkimage = return_status['myimage']
        checktransfert = return_status['myimgstatus']
        installPercent = return_status['percent_install']


        print (f'{checktransfert} : {installPercent}%')
        loops=0
        while checkstate == "INSTALL_IDLE":
         return_status = check_status(remote_sw)
         checkstate = return_status['myinstall-status']
         checkimage = return_status['myimage']
         checktransfert = return_status['myimgstatus']
         installPercent = return_status['percent_install']

         if checktransfert == "TRANSFER_FILE_EXTRACTION":
          print(f'{checktransfert}')

         elif checktransfert == "TRANSFER_VALIDATION" and installPercent ==100:
          print(f'Check CRC in progress {loops}')
          loops = loops + 1
          if loops >200:
           result_cancel = cancel_install(remote_sw)
           result = 'FAIL'
           break

          else:
           print(f'{checktransfert} : {installPercent}%')

        while checkstate == "INSTALL_PROGRESS":
         return_status = check_status(remote_sw)
         checkstate = return_status['myinstall-status']
         print(f'Please wait : {checkstate}')

        if checkstate == "INSTALL_STATE_SUCCESS":
         print(f'Next step Boot Swap')
         return_status = check_status(remote_sw)
         checkimage = return_status['myimage']
         result = bootswap(remote_sw, firmware=checkimage)
         if result == "SUCCESS":
          print(f'Boot Order change: {result}')
          return_boot = check_boot_order(remote_sw)
          boot_next = return_boot['next']
          print(f'next-boot : {boot_next}')

        if result == "FAIL":
         print(f'Check CRC {result} for {filename}, Install Cancelation {result_cancel}')


       else:
         print("IP address is not valid or unreachable\r\nUse rpc_update.py -h for Help")

if __name__ == '__main__':
    main()
