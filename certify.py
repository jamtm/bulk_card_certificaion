#!/usr/bin/env python

import csv
import logging
import subprocess
import os
import argparse
import getpass
import configparser

"""
################################################################################
#                        DOMO AUTO CARD CERTIFIER                              #
#                                                                              #
# This script automates the process of requesting and certifying cards         #
#                        in a Domo instance.                                   #
#                                                                              #
# It contains 2 functions '                                                    #
#                                                                              #
# Usage:                                                                       #
#   python certify.py submit_certification <Username>                          #
#                                                                              #
#                                                                              #
# Example:                                                                     #
#   python certify.py --function submit_certification john.doe@domo.com        #
#                                      or                                      #
#   python certify.py --function approve_certification john.doe@domo.com       #
#                                                                              #
# After executing the script, you will be prompted for your Domo password.     #
#                                                                              #
################################################################################
"""

config = configparser.ConfigParser()
config.read('config.ini')

# ---- VARIABLES ----- #
domo_instance = config.get('DEFAULT', 'domo_instance')
certification_id = config.get('DEFAULT', 'certification_id')
card_list_dataset_id = config.get('DEFAULT', 'card_list_dataset_id')

log_file = 'process.log'
logging.basicConfig(level=logging.DEBUG, filename=log_file, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')


def request_certification(username, pwd):
    create_output_files(username, pwd, 'get_card_list', '')
    execute_command(domo_instance, f'cli_script_files/{domo_instance}_get_card_list')
    with open(f'cli_script_files/{domo_instance}_cards_to_certify.csv', 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip header row
        for row in reader:
            card_id = row[0]
            create_output_files(username, pwd, 'request_certification', card_id)
            execute_command(domo_instance, f'cli_script_files/{domo_instance}_request_certification_card_{card_id}')
            os.remove(f'cli_script_files/{domo_instance}_request_certification_card_{card_id}')
    cleanup(domo_instance, "request_certification")


def approve_certification(username, pwd):
    create_output_files(username, pwd, 'get_approvals', '')
    execute_command(domo_instance, f'cli_script_files/{domo_instance}_approval_list')
    with open(f'cli_script_files/{domo_instance}_approval_id_list.csv', 'r') as file:
        row = file.readline().strip()
        values = row.split(',')
        for value in values:
            approval_id = value
            print(approval_id)
            create_output_files(username, pwd, 'approve_certification', approval_id)
            execute_command(domo_instance, f'cli_script_files/{domo_instance}_approve_cert_request_{approval_id}')
            os.remove(f'cli_script_files/{domo_instance}_approve_cert_request_{approval_id}')
    cleanup(domo_instance, "approve_certification")


def create_output_files(username, pwd, file_type, card_id):
    try:
        if file_type == 'get_card_list':
            with open(f"cli_script_files/{domo_instance}_get_card_list", 'w') as get_card_list:
                get_card_list.write(f"connect -u {username} -p {pwd} -s {domo_instance}.domo.com\n")
                get_card_list.write(f"query-data -i {card_list_dataset_id} -xf cli_script_files/{domo_instance}_cards_to_certify.csv -sql \"SELECT `Card ID`, `Title` FROM `{card_list_dataset_id}`\" \n")
            logging.info(f"File {domo_instance}_get_card_list created successfully")

        if file_type == 'request_certification':
            with open(f"cli_script_files/{domo_instance}_request_certification_card_{card_id}", 'w') as request_certification:
                request_certification.write(f"connect -u {username} -p {pwd} -s {domo_instance}.domo.com\n")
                request_certification.write(f"request-certification -i {certification_id} -c {card_id} \n")
                logging.info(f"File {domo_instance}_request_certification for {card_id} created successfully")

        if file_type == 'get_approvals':
            with open(f"cli_script_files/{domo_instance}_approval_list", 'w') as approval_list:
                approval_list.write(f"connect -u {username} -p {pwd} -s {domo_instance}.domo.com\n")
                approval_list.write(f"get-needed-approvals -c 10000 -f cli_script_files/{domo_instance}_approval_id_list.csv \n")
                logging.info(f"File {domo_instance}_approval_id_list.csv created successfully")

        if file_type == 'approve_certification':
            with open(f"cli_script_files/{domo_instance}_approve_cert_request_{card_id}", 'w') as approve_cert_request:
                approve_cert_request.write(f"connect -u {username} -p {pwd} -s {domo_instance}.domo.com\n")
                approve_cert_request.write(f"approve-certification -i {card_id}""\n")
                logging.info(f"File {domo_instance}_approve_cert_request_{card_id} created successfully")
        else:
            logging.error(f"Invalid file type {file_type} provided.")
    except Exception as e:
        logging.error(f"An error occurred while creating files for  {domo_instance}: {e}")


def execute_command(instance, script_file):
    proc = subprocess.Popen(['java', '-jar', 'domoUtil.jar', '-script', script_file])
    proc.wait()
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        logging.error(f"Error executing command for {instance}: {stderr}")
    else:
        logging.info(f"Command executed successfully for {instance}: {stdout}")


def cleanup(instance, function):
    if function == "request_certification":
        os.remove(f"cli_script_files/{instance}_get_card_list")
        os.remove(f"cli_script_files/{instance}_cards_to_certify.csv")
    elif function == "approve_certification":
        os.remove(f"cli_script_files/{domo_instance}_approval_id_list.csv")
        os.remove(f"cli_script_files/{domo_instance}_approval_list")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Certify Cards: A script to certify cards in Domo. There are two '
                                                 'functions available, one to submit cards for approval ciontains within'
                                                 ' your Domo dataset \'submit_certification\', and one approve all '
                                                 'pending certification requests of the person running the script'
                                                 ' \'approve_certification\'. Use the following formatsL: python'
                                                 ' certify.py --function submit_certification your.name@company.com '
                                                 ' or python certify.py --function approve_certification'
                                                 ' your.name@company.com after you run this, you will be asked for your'
                                                 ' password. Make sure your variables are set in the config.ini file.')
    parser.add_argument('--function', type=str, required=True, help='Function to run', choices=['submit_certification', 'approve_certification'])
    parser.add_argument('username', type=str, help='Username')
    args = parser.parse_args()
    pwd = getpass.getpass(prompt='Domo Password: ')

if args.function == 'submit_certification':
    request_certification(args.username, pwd)
elif args.function == 'approve_certification':
    approve_certification(args.username, pwd)




