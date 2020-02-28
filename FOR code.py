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
                # print(", ".join(row))
                line_count += 1
                print(row[1], row[3])
                fetchDataset(row[1], row[3])
        print(f'Processed {line_count} lines.')


def fetchDataset(doi, forCode):
    entries = (
        'id', 'versionNumber', 'versionMinorNumber', 'versionState', 'productionDate', 'lastUpdateTime', 'releaseTime',
        'createTime', 'UNF', 'files')
    try:
        r = requests.get(Constants.API_FETCHDATASET + doi, headers=Constants.API_WP_POSTS_HEADER)
        print("fetch " + str(r.status_code))
        if r.status_code == 200:
            res = json.loads(r.text)
            updateJSON = res['data']['latestVersion']
            for k in entries:
                updateJSON.pop(k, None)
            # print(updateJSON)
            # updateJSON['metadataBlocks']['citation']['fields'][0]['value'] = forCode
            fields = editDataset(updateJSON, forCode)
            # print(fields)
            updateJSON['metadataBlocks']['citation']['fields'] = fields
            updateDataset(doi, updateJSON)
    except Exception as error:
        print('ERROR', error)


def editDataset(dataset, forCode):
    fields = dataset['metadataBlocks']['citation']['fields']
    # print(fields)
    topicJSON = {"typeName": "topicClassification",
                 "multiple": True,
                 "typeClass": "compound",
                 "value": [
                     {"topicClassValue":
                         {
                             "typeName": "topicClassValue",
                             "multiple": False,
                             "typeClass": "primitive",
                             "value": "16"
                         }
                     }
                 ]
                 }

    # topicJSON = json.loads(topicClassification)
    for i in fields:
        if i['typeName'] == 'topicClassification':
            if i['multiple']:
                i['value'][0]['topicClassValue']['value'] = forCode
                print("Found topicClassification true")
                return fields
            else:
                i['value']['topicClassValue']['value'] = forCode
                print("Found topicClassification false")
                return fields
    print("not found")
    topicJSON['value'][0]['topicClassValue']['value'] = forCode
    fields.append(topicJSON)
    return fields


def updateDataset(doi, data):
    try:
        r = requests.put(Constants.API_UPDATEDATASET + doi, data=json.dumps(data, ensure_ascii=False),
                         headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)

        print("update " + str(r.status_code))
        publishDataset(doi)
    except Exception as error:
        print(error)


def publishDataset(doi):
    try:
        r = requests.post(Constants.API_PUBLISHDATASET + doi + "&type=minor",
                          headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)
        print("publish " + str(r.status_code))
        print("Done")
    except Exception as error:
        print('ERROR', error)


def main():
    print(str(currentDateTime()) + " Executing...")
    readCSV()
    # print(fetchDataset('doi:10.5072/FK2/XS0BPD', '02'))


if __name__ == "__main__":
    main()
