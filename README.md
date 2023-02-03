# Domo Bulk Card Certifier

A python script to automate the process of requesting certification and approving certification of cards in a Domo instance. 
The script contains two functions, one to allow you to submit cards for certification and one to approve any pending certification requests.

Before using this we recommend that you are familiar with the certification process within Domo, you can view details for this here: https://domo-support.domo.com/s/article/360043430613?language=en_US 

## Setup

There are a some configuration steps to complete before we run the script, namely gathering up some GUIDs from your Domo instance to enter in to a configuration file for the script to reference. 

### 1. Create a dataset of cards to be certified.
Our recommendation is to create a dataset view on top of the 'Domo Governance Datasets Connector' with the 'Cards' report selected. 
Filter your dataset view so that the resulting dataset contains the list of cards you would like to request certification for.

NOTE: Only the card owner is able to request certification, so we recommend applying a filter on the 'Owner Name' column to the person who will be executing the script and requesting the certification.

The script expects 2 columns to be present, 'Card ID' and 'Title'. These are two of the default columns in the Governance Dataset for listing Cards.

Once your dataset view is created, containing the list of cards to request certification for, take a note of the Dataset ID / Dataset GUI (located in the URL when viewing the dataset view) this is your *'card_list_dataset_id'* value. (it will be in a similar format to this: *d99365a7-864a-435d-92f7-d8b12f2bf47b*)  

   
### 2. Locate the GUID for the Certification Process.
Within Domo it is likely you have multiple certification options / departments to choose from when requesting certification for a card. We will need to locate the GUID of the Certification you wish to use.

You can view all of the Certification departments at this link (swapping your instance name):https://domo_instance.domo.com/admin/certifiedcontent/certified-cards
Select and open the department certification process you wish the script to use and, like with the dataset view, locate and copy the GUID from the URL bar. make a note of this GUID this is your *certification_id* value. 

### 2. Clone this repository
Or download it to your local machine.

### 2. Download the latest Java CLI Utility
From this link: https://app.domo.com/labs/java-sdk/latest/domoUtil.jar and place it in the root directory. 

### 3. Edit and populate the 'config.ini' file.
Open up the config.ini file with a text editor and populate the variables with the information you gathered in steps 1 and 2.
domo_instance is the URL you use to log in to Domo (excluding the '.domo.com' part)
ceertification_id is the GUID of the certification path from step 2
card_list_dataset_id is the GUID of your dataset containing cards to cetify.

#### Example Config.ini file:
```
[DEFAULT]
domo_instance = acme-corp
certification_id = d99365a7-864a-435d-92f7-d8b12f2bf47b
card_list_dataset_id = b93109f2-3c3f-4dba-9493-98ef8991687e
```


## Executing

Ensure you have python installed on your machine, the script uses the following dependencies:

```
import csv
import logging
import subprocess
import os
import argparse
import getpass
import configparser
```

The script has a help file available you can call this using the following:
```
python certify.py -h
```

The script contains 2 functions, one to submit the cards for certification and one to approve.
Only the card owner may submit the cards for approval and only the next person in the approval chain may approve them. The script uses username and password authentication, since this a requirement for using the certification process within Domo.

To submit all cards in the dataset for approval execute the following, where the email address is the email you use to log in to Domo.
```
python certify.py --function submit_certification firstname.secondname@companyname.com
```

If you wish to approve any card certification requests that have been submitted and are pending you approval you can run the following command to approve all of them.
*Note: this command does not use the 'card_list_dataset_id' or the 'certification_id' variables.*

```
python certify.py --function approve_certification firstname.secondname@companyname.com
```

## Notes
- The script will create an write out each step it performs to a process.log file. This will be replaced upon each execution of the script.

- While the script runs it will create a number of local temporary files and will execute the CLI Utility a number of times. All temporary files will be removed at the end of its execution.

- The script can approve up to 10,000 cards per execution. 





