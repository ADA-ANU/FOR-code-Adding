#!/usr/bin/env python
import urllib
import requests
import json
import Constants
from datetime import datetime
from time import sleep
import csv


newlyPublished = []
newlyUpdated = []
wpToken = ""
waitingToTweet = []
Pcount = 0
Ucount = 0

def currentDateTime():
    d_naive = datetime.now()

    return d_naive


def readCSV():
    with open('Book1.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('Column names are' + ", ".join(row))
                line_count += 1
            else:
                print(", ".join(row))
                line_count += 1
        print(f'Processed {line_count} lines.')


def fetchDataset(doi, forCode):

    try:
        r = requests.get(Constants.API_FETCHDATASET+doi, headers=Constants.API_WP_POSTS_HEADER)
        print(r.status_code)
        if r.status_code == 200:
            res = json.loads(r.text)
            # print(res['data']['latestVersion']['metadataBlocks']['citation']['fields'][7]['value'][0]['topicClassValue']['value'])
            # print(res['data']['latestVersion']['metadataBlocks'])
            data = {"termsOfUse": "Conditions of use:</p>\r\n\r\nI acknowledge that:</p>\r\n\r\n1. Use of the material is restricted to use for analytical purposes and that this means that I can only use the material to produce information of an analytical nature. Examples of such uses are:\r\n(a) the manipulation of data to produce means, correlations or other descriptive summary measures; \r\n(b) the estimation of population characteristics from sample data;\r\n(c) the use of data as input to mathematical models and for other types of analyses (e.g. factor analysis); and \r\n(d) to provide graphical and pictorial representation of characteristics of the population or sub-sets of the population. </p>\r\n\r\n2. The material is not to be used for any non-analytical purposes, or for commercial or financial gain, without the express written permission of the Australian Data Archive. Examples of non-analytical purposes are: \r\n(a) transmitting or allowing access to the data in part or whole to any other person / Department / Organisation not a party to this undertaking; and \r\n(b) attempting to match unit record data in whole or in part with any other information for the purposes of attempting to identify individuals. </p>\r\n\r\n3. Outputs (such as statistics, tables and graphs) obtained from analysis of these data may be further disseminated provided that I: \r\n(a) acknowledge both the original depositors and the Australian Data Archive; \r\n(b) acknowledge another archive where the data file is made available through the Australian Data Archive by another archive; and \r\n(c) declare that those who carried out the original analysis and collection of the data bear no responsibility for the further analysis or interpretation of it.\r\n4. Use of the material is solely at my risk and I indemnify the Australian Data Archive and its host institution, The Australian National University. <p> 5. The Australian Data Archive and its host institution, The Australian National University, shall not be held liable for any breach of this undertaking. <p> 6. The Australian Data Archive and its host institution, The Australian National University, shall not be held responsible for the accuracy and completeness of the material supplied.<p>",
"confidentialityDeclaration": "You will also need to complete a signed General Undertaking form if this is the first time you will be downloading data from the Australian Data Archive.",
"specialPermissions": "None",
"restrictions": "The depositor may be informed (by the archive) of use being made of the data, in order to comment on that use and make contact with colleagues of similar interests.",
"citationRequirements": "All manuscripts based in whole or in part on these data should: (i) identify the data and original investigators by using the recommended bibliographic reference to the data file; (ii) acknowledge the Australian Data Archive and, where the data are made available through the Australian Data Archive by another archive, acknowledge that archive; (iii) declare that those who carried out the original analysis and collection of the data bear no responsibility for the further analysis or interpretation of them.",
"depositorRequirements": "In order to assemble essential information about archival resources and to facilitate the exchange of information about users’ research activities, individuals are required to email ADA (ada@anu.edu.au) with the bibliographic details and, where available, online links to any published work (including journal articles, books or book chapters, conference presentations, theses or any other publications or outputs) based wholly or in part on the material.",
"disclaimer": "Use of the material is solely at the user's risk. The depositor, The Australian National University and the Australian Data Archive shall not be held responsible for the accuracy and completeness of the material supplied.","metadataBlocks": res['data']['latestVersion']['metadataBlocks']}
            data['metadataBlocks']['citation']['fields'][7]['value'][0]['topicClassValue']['value'] = forCode
            # print(data['metadataBlocks']['citation']['fields'][7]['value'][0])
            updateDataset(doi, data)
    except Exception as error:
        print('ERROR', error)



def updateDataset(doi, data):

    # print(url)
    # print("https://dataverse-dev.ada.edu.au/api/datasets/2058/versions/:draf")
    # script_dir = os.path.dirname(__file__) + "/dataset-update-metadata.json"
    # with open(script_dir, 'r+') as f:
    #     data = json.load(f)
    #     data["metadataBlocks"]["citation"]["fields"][0]["value"] = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    #     print()

    try:
        r = requests.put(Constants.API_UPDATEDATASET + doi, data=json.dumps(data), headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)

        print(r.status_code)
        print(json.loads(r.text))
        res = json.loads(r.text)

        publishDataset(doi)
    except Exception as error:
        print('ERROR', error)


def publishDataset(doi):
    try:
        r = requests.post(Constants.API_PUBLISHDATASET + doi + "&type=minor", headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)
        print(r.status_code)
        print(json.loads(r.text))
    except Exception as error:
        print('ERROR', error)


def main():
    print(str(currentDateTime()) + " Executing...")
    readCSV()
    print(fetchDataset('doi:10.5072/FK2/XS0BPD', '16'))


if __name__ == "__main__":
    main()




