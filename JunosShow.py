from multiprocessing import Queue, Process
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException, NetMikoAuthenticationException
from datetime import datetime
from getpass import getpass
import csv
import logging


def help_commands():
    print('Show commands available:\n\n'
          '   arp - Shows ARP on all devices,\n'
          '         (This command takes time and may cause timeout on some devices.)\n'
          '   bgp - Shows all BGP peers, summary statement is assumed.\n'
          '   chassis - Shows the chassis hardware information.\n'
          '   chassis alarms - Shows the chassis alarms on one or many devices.\n'
          '   configuration - Shows configuration in the display set format.\n'
          '   custom - Allows a custom show command. Do not add the show statement\n'
          '            since it is already added for you.\n'
          '            ex: ntp associations, security ipsec security-associations \n'
          '   inspection - Inspect a single device showing a wide range of criteria\n'
          '                and outputs the information to a file.\n'
          '   interfaces - Shows interfaces in terse.\n'
          '   interfaces up - Shows interfaces that are up.\n'
          '   interfaces down - Shows interfaces that are down.\n'
          '   ospf - Shows all OSPF neighbor information the neighbor statement is assumed.\n'
          '   security ipsec - Shows ipsec for SRX\'s only.\n'
          '   services ipsec - Shows ipsec for M series devices only.\n'
          '   system alarms - Shows the system alarms on one or many devices.\n'
          '   version - Shows the version on the device.\n'
          '   vlans - Shows switch vlan information.\n\n')


class JunosShow:

    def __init__(self, username, password, ip, show_command):
        self.user = username
        self.passw = password
        self.ip_add = ip
        self.show = show_command

    def junos_device_inspection(self):
        print('Enter the target IP you would like to run this inspection on. \n CTRL-C to cancel at anytime\n')
        ip = input('ip: ')
        device = {
            'device_type': 'juniper',
            'ip': ip,
            'username': self.user,
            'password': self.passw
        }
        try:
            print('Device inspection requires output to a file.\n Please enter the output filename.\n')
            filename = input('Filename:')
            save_file = open(f'output\{filename}.txt', mode='w')
            print(f"\n--------------- Begin {ip} ---------------")
            print('Running Inspection process.....')
            net_connect = ConnectHandler(**device, global_delay_factor=4, timeout=60)
            version = net_connect.send_command('show version')
            chassis_hardware = net_connect.send_command('show chassis hardware')
            chassis_alarms = net_connect.send_command('show chassis alarms')
            system_alarms = net_connect.send_command('show system alarms')
            interfaces_terse = net_connect.send_command('show interfaces terse')
            descriptions = net_connect.send_command('show interfaces descriptions')
            interfaces = net_connect.send_command('show interfaces')
            print('Almost Done.')
            routing_engine = net_connect.send_command('show chassis routing-engine')
            environment = net_connect.send_command('show chassis environment')
            storage = net_connect.send_command('show system storage')
            commits = net_connect.send_command('show system commit')
            boot_messages = net_connect.send_command('show system boot-messages')
            ntp_associations = net_connect.send_command('show ntp associations')
            ntp_status = net_connect.send_command('show ntp status')
            print('Show commands complete Finalizing.')
            net_connect.disconnect()
            print(f"--------------- END {ip} ---------------\n")
            save_file.write(f'#############{ip}############')
            save_file.write('\n-------Version-------')
            save_file.write(f'{version}')
            save_file.write('\n------- Chassis Hardware -------')
            save_file.write(f'{chassis_hardware}')
            save_file.write('\n------- Chassis Alarms -------')
            save_file.write(f'{chassis_alarms}')
            save_file.write('\n------- System Alarms -------')
            save_file.write(f'{system_alarms}')
            save_file.write('\n------- Interfaces Terse -------')
            save_file.write(f'{interfaces_terse}')
            save_file.write('\n------- Interface Descriptions -------')
            save_file.write(f'{descriptions}')
            save_file.write('\n------- Interfaces -------')
            save_file.write(f'{interfaces}')
            save_file.write('\n------- Routing Engine -------')
            save_file.write(f'{routing_engine}')
            save_file.write('\n------- Environment -------')
            save_file.write(f'{environment}')
            save_file.write('\n------- System Storage -------')
            save_file.write(f'{storage}')
            save_file.write('\n------- Commits -------')
            save_file.write(f'{commits}')
            save_file.write('\n------- Boot Messages -------')
            save_file.write(f'{boot_messages}')
            save_file.write('\n------- NTP Associations -------')
            save_file.write(f'{ntp_associations}')
            save_file.write('\n------- NTP Status-------')
            save_file.write(f'{ntp_status}')
            save_file.write(f'###################{ip}###############')
            save_file.close()
            print("##########################################################\n\n"
                  f"Complete! See output\{filename}.txt to review the output!\n"
                  "##########################################################\n")
        except NetMikoTimeoutException:
            print(f"SSH is not working to {ip}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {ip}. Insure device is reachable."
                            "Verify CSV file has the correct IP.")
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password. Make sure you have an account on {ip}.")
            logging.warning(f"{datetime.now()}: Check your username/password."
                            " Make sure you have an account on this device.")
        except ValueError:
            print(f'There has been an error ensure you have the correct permissions to run this command. on {ip}')
            logging.warning(f'{datetime.now()}: Check your username/password.'
                            f' Make sure you have the correct permissions to access {ip}.')

    def junos_config(self, today, device, hostname):
        logging.basicConfig(filename='logs\JunosShowFailure.log', level=logging.WARNING)
        # Turns on logging to a file named JunosShowFailure.
        try:
            save_file = open(f'output\configs\{hostname} {today}.txt', mode='w')
            net_connect = ConnectHandler(**device, timeout=60)
            output = f"\n--------------- Begin {hostname} ---------------"
            output += net_connect.send_command(f'show {self.show}')
            output += f"--------------- END {hostname} ---------------\n"
            net_connect.disconnect()
            print(output)
            save_file.write(output)
            save_file.close()
        except NetMikoTimeoutException:
            print(f"SSH is not working to {hostname}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {hostname}. Insure device is reachable."
                            "Verify correct IP in [juniper devices.csv]")
            pass
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password for {hostname}. Make sure you have an account on this device.")
            logging.warning(f"{datetime.now()}: Check your username/password for {hostname}."
                            " Make sure you have an account on this device.")
            pass
        except ValueError:
            print(f'There has been an error ensure you have the correct permissions to run this command. on {hostname}')
            logging.warning(f'{datetime.now()}: Check your username/password.'
                            f' Make sure you have the correct permissions to access {hostname}.')
            pass

    def junos_command(self, today, device, filename, hostname):
        logging.basicConfig(filename='logs\JunosShowFailure.log', level=logging.WARNING)
        # Turns on logging to a file named JunosShowFailure.
        try:
            save_file = open(f'output\{filename} {today}.txt', mode='a')
            net_connect = ConnectHandler(**device, timeout=60)
            output = f"\n--------------- Begin {hostname} ---------------"
            output += net_connect.send_command('show ' + self.show)
            output += f"--------------- END {hostname} ---------------\n"
            net_connect.disconnect()
            print(output)
            save_file.write(output)
            save_file.close()
        except NetMikoTimeoutException:
            print(f"SSH is not working to {hostname}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {hostname}. Insure device is reachable."
                            "Verify correct IP in [juniper devices.csv]")
            pass
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password for {hostname}. Make sure you have an account on this device.")
            logging.warning(f"{datetime.now()}: Check your username/password for {hostname}."
                            " Make sure you have an account on this device.")
            pass
        except ValueError:
            print(f'There has been an error ensure you have the correct permissions to run this command. on {hostname}')
            logging.warning(f'{datetime.now()}: Check your username/password.'
                            f' Make sure you have the correct permissions to access {hostname}.')
            pass

    def junos_show_many(self, set_dev_type, srx_non_srx):
        today = datetime.now().strftime('%Y%m%d-%H%M')
        start = datetime.now()
        Queue(maxsize=20)
        process = []
        filename = ''
        if 'configuration' in self.show:
            pass
        else:
            filename = input('\nFilename for output: ')
        with open("DeviceDB.csv", mode='r') as devices:
            reader = csv.DictReader(devices)
            for row in reader:
                device_type = row['device_type']
                ip = row['IP_Address']
                hostname = row['HostName']
                dev_type = row['dev_type']
                srx = row['srx']
                device = {
                    'device_type': device_type,
                    'ip': ip,
                    'username': self.user,
                    'password': self.passw,
                }
                if device_type == 'juniper':
                    pass
                else:
                    continue
                if dev_type == set_dev_type and srx == srx_non_srx:
                    pass
                elif dev_type == set_dev_type and srx_non_srx == '':
                    pass
                elif set_dev_type == '' and srx_non_srx == '':
                    pass
                else:
                    continue
                if 'configuration' in self.show:
                    my_process = Process(target=self.junos_config, args=(today, device, hostname))
                    my_process.start()
                    process.append(my_process)
                else:
                    my_process = Process(target=self.junos_command,
                                         args=(today, device, filename, hostname))
                    my_process.start()
                    process.append(my_process)

        for a_process in process:
            a_process.join()

        end_time = datetime.now() - start
        print(f'Total time to run = {end_time}')
        print("##########################################################\n\n"
              f"Complete! See output folder to review the output!\n\n"
              "##########################################################\n")

    def junos_show_one(self):
        logging.basicConfig(filename='logs\JunosShowFailure.log', level=logging.WARNING)
        # Turns on logging to a file named JunosShowFailure.
        device = {
            'device_type': 'juniper',
            'ip': self.ip_add,
            'username': self.user,
            'password': self.passw
        }
        try:
            save = input('Would you like to save this output to a file? (yes/no)')
            if save.lower() == 'yes' or save.lower() == 'y':
                filename = input('Filename:')
                save_file = open(f'output\{filename}.txt', mode='w')
                net_connect = ConnectHandler(**device)
                show = net_connect.send_command(f'show {self.show}')
                net_connect.disconnect()
                print(f"\n--------------- Begin {self.ip_add} ---------------")
                print(show)
                print(f"--------------- END {self.ip_add} ---------------\n")
                save_file.write(f'#############{self.ip_add}############')
                save_file.write(f'{show}')
                save_file.write(f'###################{self.ip_add}###############')
                save_file.close()
                print("##########################################################\n\n"
                      f"Complete! See output\{filename}.txt to review the output!\n"
                      "##########################################################\n")
            else:
                net_connect = ConnectHandler(**device)
                show = net_connect.send_command(f'show {self.show}')
                net_connect.disconnect()
                print(f"\n--------------- Begin {self.ip_add} ---------------")
                print(show)
                print(f"--------------- END {self.ip_add} ---------------\n")
        except NetMikoTimeoutException:
            print(f"SSH is not working to {self.ip_add}. Insure device is reachable")
            logging.warning(f"{datetime.now()}: SSH is not working to {self.ip_add}. Insure device is reachable."
                            "Verify CSV file has the correct IP.")
        except NetMikoAuthenticationException:
            print(f"Check your Username/Password. Make sure you have an account on this device.")
            logging.warning(f"{datetime.now()}: Check your username/password."
                            " Make sure you have an account on this device.")
        except ValueError:
            print('There has been an error ensure you have the correct permissions'
                  f' to run this command. on {self.ip_add}')
            logging.warning(f'{datetime.now()}: Check your username/password.'
                            f' Make sure you have the correct permissions to access {self.ip_add}.')


def junos_show():
    username = input('Username: ')
    password = getpass('Password: ')
    print('Insert the show command you wish to run.')
    loop = True
    show_command = ''
    set_dev_type = ''
    srx_non_srx = ''
    while loop:
        command = input("Show:")
        if command.lower() == 'help'or command == '?':
            help_commands()
        elif command == '':
            pass
        elif command.lower() == 'exit':
            return
        elif command.lower() == 'arp':
            print('Arp may have a hard time showing on some devices keep an eye out for failures.')
            show_command = 'arp'
            loop = False
        elif command.lower() == 'bgp':
            set_dev_type = 'router'
            show_command = 'bgp summary'
            loop = False
        elif command.lower() == 'chassis alarms':
            show_command = 'chassis alarms'
            loop = False
        elif command.lower() == 'chassis':
            show_command = 'chassis hardware'
            loop = False
        elif command.lower() == 'configuration':
            show_command = 'configuration | display set | no-more'
            loop = False
        elif command.lower() == 'custom':
            question = input('Show on Router or Switch? ')
            if question.lower() == 'router':
                set_dev_type = 'router'
                srx = input('Is this an srx or nonsrx? ')
                if srx.lower() == 'srx':
                    srx_non_srx = 'srx'
                elif srx.lower() == 'nonsrx':
                    srx_non_srx = 'nonsrx'
                else:
                    srx_non_srx = ''
            elif question.lower() == 'switch':
                set_dev_type = 'switch'
            else:
                set_dev_type = ''
            print('\n Enter the command without the word show.\n')
            show_command = input('show ')
            loop = False
        elif command.lower() == 'inspection':
            JunosShow(username, password, ip='', show_command='').junos_device_inspection()
        elif command.lower() == 'interfaces':
            show_command = 'interfaces terse'
            loop = False
        elif command.lower() == 'interfaces up':
            show_command = 'interfaces terse| match "ge-|fe-|lo0.0|gr-|te|st0|sp-|vlan|ae|reth" | match "up    up"'
            loop = False
        elif command.lower() == 'interfaces down':
            show_command = 'interfaces terse| match "ge-|fe-|lo0.0|gr-|te|st0|sp-|vlan|ae|reth" | match "up    down"'
            loop = False
        elif command.lower() == 'ospf':
            set_dev_type = 'router'
            show_command = 'ospf neighbor'
            loop = False
        elif command.lower() == 'security ipsec':
            set_dev_type = 'router'
            srx_non_srx = "srx"
            show_command = 'security ipsec security-associations'
            loop = False
        elif command.lower() == 'services ipsec':
            set_dev_type = 'router'
            srx_non_srx = "nonsrx"
            show_command = 'services ipsec-vpn ipsec security-associations'
            loop = False
        elif command.lower() == 'system alarms':
            show_command = 'system alarms'
            loop = False
        elif command.lower() == 'version':
            show_command = 'version'
            loop = False
        elif command.lower() == 'vlans':
            set_dev_type = 'switch'
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
            JunosShow(username, password, ip, show_command).junos_show_one()
            end_time = datetime.now()
            total_time = end_time - start_time
            one_or_all_q = False
        elif one_or_all.lower() == "all":
            print(f'All {set_dev_type} devices will be issued {command}.\n\n')
            start_time = datetime.now()
            ip = ''
            JunosShow(username, password, ip, show_command).junos_show_many(set_dev_type, srx_non_srx)
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
    junos_show()