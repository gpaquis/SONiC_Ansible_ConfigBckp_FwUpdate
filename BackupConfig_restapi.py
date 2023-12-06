import json
import argparse
import ast
import os.path
import requests
import configparser
import ipaddress
from datetime import datetime
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

    switch_ip = remote_sw['switch_ip']
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

def read_config():

    sw_list = dict()
    backup_cfg = []
    config = configparser.ConfigParser()
    config.read('backup_list.conf')

    for each_section in config.sections():
      for (each_key, each_val) in config.items(each_section):
          if each_key == "docker-name":
              tpcmlist.update({each_section : each_val})
    print (f'{tpcmlist}')
    myanswer = input('Enter TPCM id (ex: TPCM1) or ALL:')
    if myanswer.lower() != "all":
     tpcmreturn.append(myanswer.upper())
     #print (f'install: {myanswer}')
     return tpcmreturn
    else:
        for each_section in tpcmlist:
         #print (f'{each_section}')
         tpcmreturn.append(each_section)
        return tpcmreturn

def backup_config(remote_sw,remote_srv):
    """
      source:  alway "config://config.db.json"
      destination: method://rem_login:rem_passwd@rem_serv/rem_path/filename+timestamps.json
      copy-config-option: MERGE
    """
    switch_ip = remote_sw['switch_ip']
    user_name = remote_sw['sonic_username']
    password = remote_sw['sonic_password']

    method = remote_srv['method']
    rem_serv = remote_srv['remote_server']
    rem_login = remote_srv['remote_login']
    rem_passwd = remote_srv['remote_passwd']
    rem_path = remote_srv['remote_path']

    FORMAT = '%Y%m%d%H%M'
    timestamp = datetime.now().strftime(FORMAT)

    filename = switch_ip + '_' + timestamp + '.json'
    print(filename)
    full_path = method + "://" + rem_login + ":" + rem_passwd + "@" + rem_serv + rem_path + '/' + filename
    print(f'{full_path}')

    request_data = {
        "openconfig-file-mgmt-private:input": {
           "source": "config://config_db.json",
           "destination": full_path,
           "copy-config-option": "MERGE"
        }
    }





    try:
       response = requests.post(url=f"https://{switch_ip}/restconf/operations/openconfig-file-mgmt-private:copy",
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
        mystatus = json.loads(response.content)
        myreturn = mystatus["openconfig-file-mgmt-private:output"]["status-detail"]
        return myreturn

def main():
    parser = argparse.ArgumentParser(description='Backup config file tools')
    parser.add_argument("--method", help="ftp or scp", type=str)
    parser.add_argument("--switch_ip", help="IP address of the switch", type=str)
    parser.add_argument("--sonic_username", help="SONiC Login", type=str)
    parser.add_argument("--sonic_password", help="SONiC Password", type=str)
    parser.add_argument("--remote_server", help="Remote server IP", type=str)
    parser.add_argument("--remote_login", help="Remote server login", type=str)
    parser.add_argument("--remote_password", help="Remote server Password", type=str)
    parser.add_argument("--remote_path", help="Remote path", type=str)
    parser.add_argument("--bulk", help="config filename for bulk backup", type=str)
    args = parser.parse_args()

    method = args.method.lower()
    switch_ip = args.switch_ip
    sonic_username = args.sonic_username
    sonic_password = args.sonic_password
    remote_server = args.remote_server
    remote_login = args.remote_login
    remote_passwd = args.remote_password
    remote_path = args.remote_path



    config = args.bulk
    if config == None:
      switch_ip = args.switch_ip
      rem_srv = args.remote_server
    else:
      check_file = os.path.exists(config)
      if check_file == True:
        print ('tot')

    if validate_ip_address(switch_ip) == True and validate_ip_address(remote_server) == True :
      remote_sw = {'switch_ip':switch_ip, 'sonic_username':sonic_username, 'sonic_password':sonic_password}
      remote_srv = {'method':method, 'remote_server':remote_server, 'remote_login':remote_login, 'remote_passwd':remote_passwd, 'remote_path':remo
te_path}

    if method == "scp" or "ftp":
        result = backup_config(remote_sw, remote_srv)
        print(f'Backup {switch_ip} : {result}')

    else:
         print("IP address is not valid or unreachable\r\nUse rpc_update.py -h for Help")

if __name__ == '__main__':
    main()
