from multiprocessing import Queue, Process
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, NetMikoAuthenticationException
from datetime import datetime
from getpass import getpass
import csv
import logging


class CiscoShow:

    def __init__(self, username, password, ip, show_command):
        self.user = username
        self.passw = password
        self.ip_add = ip
        self.show = show_command

    def configuration(self, today, device, hostname):
        logging.basicConfig(filename='logs\CiscoShowFailure.log', level=logging.WARNING)
        try:
            save_file = open(f'output\Configs\{hostname} {today}.txt', mode='w')
            net_connect = ConnectHandler(**device, timeout=60)
            output = f"\n==================== Begin {hostname} ====================\n"
            output += net_connect.send_command(f'show {self.show}')
            output += f"\n====================  End  {hostname} ====================\n"
            net_connect.disconnect()
            print(output)
            save_file.write(output)
            save_file.close()
        except NetMikoTimeoutException:
            print(f"SSH is not working to {hostname}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {hostname}. Insure device is reachable."
                            "Verify correct IP in [juniper devices.csv]")
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password on {hostname}. Make sure you have an account on this device.")
            logging.warning(f"{datetime.now()}: Check your username/password on {hostname}."
                            " Make sure you have an account on this device.")
        except ValueError:
            print('There has been an error ensure you have the correct permissions to run this command.')
            logging.warning(f"{datetime.now()}: Check your username/password."
                            " Make sure you have the correct permissions to access this device.")

    def command(self, today, device, filename, hostname):
        logging.basicConfig(filename='logs\CiscoShowFailure.log', level=logging.WARNING)
        try:
            save_file = open(f'output\{filename} {today}.txt', mode='a')
            net_connect = ConnectHandler(**device, timeout=60)
            output = f"\n==================== Begin {hostname} ====================\n"
            output += net_connect.send_command(f'show {self.show}')
            output += f"\n====================  End  {hostname} ====================\n"
            net_connect.disconnect()
            print(output)
            save_file.write(output)
            save_file.close()
        except NetMikoTimeoutException:
            print(f"SSH is not working to {hostname}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {hostname}. Insure device is reachable."
                            "Verify correct IP in [juniper devices.csv]")
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password. Make sure you have an account on this device.")
            logging.warning(f"{datetime.now()}: Check your username/password."
                            " Make sure you have an account on this device.")
        except ValueError:
            print('There has been an error ensure you have the correct permissions to run this command.')
            logging.warning(f"{datetime.now()}: Check your username/password."
                            " Make sure you have the correct permissions to access this device.")

    def all(self):
        today = datetime.now().strftime('%Y%m%d-%H%M')
        start = datetime.now()
        Queue(maxsize=20)
        process = []
        filename = ''
        if 'run' in self.show:
            pass
        else:
            filename = input('\nFilename for output: ')
        with open("DeviceDB.csv", mode='r') as devices:
            reader = csv.DictReader(devices)
            for row in reader:
                device_type = row['device_type']
                ip = row['IP_Address']
                hostname = row['HostName']
                device = {
                    'device_type': device_type,
                    'ip': ip,
                    'username': self.user,
                    'password': self.passw
                }
                if device_type == 'cisco_ios':
                    pass
                else:
                    continue
                if 'run' in self.show:
                    my_process = Process(target=self.configuration, args=(today, device, hostname))
                    my_process.start()
                    process.append(my_process)
                else:
                    my_process = Process(target=self.command, args=(today, device, filename, hostname))
                    my_process.start()
                    process.append(my_process)

        for a_process in process:
            a_process.join()

        end_time = datetime.now() - start
        print(f'Total time to run = {end_time}')
        print("##########################################################\n\n"
              f"Complete! See output folder to review the output!\n\n"
              "##########################################################\n")

    def one(self):
        today = datetime.now().strftime('%Y%m%d-%H%M')
        device = {
            'device_type': 'juniper',
            'ip': self.ip_add,
            'username': self.user,
            'password': self.passw
        }
        hostname = self.ip_add
        if 'run' in self.show:
            self.configuration(today, device, hostname)
        else:

            filename = input('\nFilename for output: ')
            self.command(today, device, filename, hostname)


def help_commands():
    print('Show commands available:\n\n'
          '   arp - Shows ARP on all devices,\n'
          '         (This command takes time and may cause timeout on some devices.)\n'
          '   bgp - Shows all BGP peers, summary statement is assumed.\n'
          '   configuration - Shows the current running configuration.\n'
          '   custom - Allows a custom show command. Do not add the show statement\n'
          '            since it is already added for you.\n'
          '            ex: ip route, ip rip \n'
          '   hardware - Shows the chassis hardware information.\n'
          '   interface brief- Shows all interface statuses.\n'
          '   interfaces up - Shows interfaces that are up.\n'
          '   interfaces down - Shows interfaces that are down.\n'
          '   ospf - Shows all OSPF neighbor information the neighbor statement is assumed.\n'
          '   ipsec - Shows ipsec security associations. \n'
          '   ntp - Shows NTP associations.\n'
          '   version - Will show the version on the device.\n'
          '   vlans - Will show device vlan information.\n\n')


def cisco_show():
    username = input('Username: ')
    password = getpass('Password: ')
    print('Insert the show command you wish to run.')
    loop = True
    show_command = ''
    while loop:
        command = input("Show: ")
        if command.lower() == 'help'or command == '?':
            help_commands()
        elif command == '':
            pass
        elif command.lower() == 'exit':
            return
        elif command.lower() == 'arp':
            show_command = 'arp'
            loop = False
        elif command.lower() == 'bgp':
            show_command = 'ip bgp summary'
            loop = False
        elif command.lower() == 'configuration':
            show_command = 'run'
            loop = False
        elif command.lower() == 'custom':
            print('\n Enter the command without the word show.\n')
            show_command = input('show ')
            loop = False
        elif command.lower() == 'hardware':
            show_command = 'hardware'
            loop = False
        elif command.lower() == 'interface brief':
            show_command = 'ip int brie'
            loop = False
        elif command.lower() == 'interfaces up':
            show_command = 'ip int brie | include  up                    up'
            loop = False
        elif command.lower() == 'interfaces down':
            show_command = 'ip int brie | include  up                    down'
            loop = False
        elif command.lower() == 'ospf':
            show_command = 'ip ospf neigh'
            loop = False
        elif command.lower() == 'ipsec':
            show_command = 'crypto ipsec sa active'
            loop = False
        elif command.lower() == 'ntp':
            show_command = 'ntp associations'
            loop = False
        elif command.lower() == 'version':
            show_command = 'version | include image'
            loop = False
        elif command.lower() == 'vlans':
            show_command = 'vlans'
            loop = False
        else:
            print('Please enter a valid show command.')
    one_or_all_q = True
    while one_or_all_q:
        one_or_all = input('Are you showing on one device or all? (one/all): ')
        if one_or_all.lower() == "one":
            ip = input('Please enter the target IP address: ')
            start_time = datetime.now()
            CiscoShow(username, password, ip, show_command).one()
            end_time = datetime.now()
            total_time = end_time - start_time
            one_or_all_q = False
        elif one_or_all.lower() == "all":
            print(f'All devices will be issued {command}.\n\n')
            start_time = datetime.now()
            CiscoShow(username, password, ip='', show_command=show_command).all()
            end_time = datetime.now()
            total_time = end_time - start_time
            one_or_all_q = False
        else:
            print("Enter a valid response.")
    print("###################################################\n\n"
          "Complete! See JunosShowFailure log for errors!\n"
          f"Total time: {total_time}\n\n"
          "###################################################\n")

if __name__ == '__main__':
    cisco_show()
