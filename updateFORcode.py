#!/usr/bin/env python
import urllib
import requests
import json
import Constants
from datetime import datetime
import csv
import time

fetchError = []
updateError = []
publishError = []
unKnownError = []
draftUpdate = []
successDatasets = []


def currentDateTime():
    d_naive = datetime.now()

    return d_naive


def readCSV():
    with open(Constants.DATASET_CSV_FILENAME) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print('Column names are: ' + ", ".join(row))
                line_count += 1
            else:
                line_count += 1
                print(row[3], row[4])
                fetchDataset(row[3], row[4].split('~'))
                print("sleep...")
                time.sleep(3)

        print(f'Processed {line_count} lines.')
        writeResult()


def writeResult():
    f = open('error.csv', 'w')
    with f:
        writer = csv.writer(f)
        writer.writerow(["Fetch error: "])
        for i in fetchError:
            writer.writerow(i)
        writer.writerow([])
        writer.writerow(["Update error: "])
        for i in updateError:
            writer.writerow(i)
        writer.writerow([])
        writer.writerow(["Publish error: "])
        for i in publishError:
            writer.writerow(i)
        writer.writerow([])
        writer.writerow(["Other error: "])
        for i in unKnownError:
            writer.writerow(i)

    f = open('success.csv', 'w')
    with f:
        writer = csv.writer(f)
        writer.writerow(["Successfully updated: "])
        for i in successDatasets:
            writer.writerow(i)
        writer.writerow([])
        writer.writerow(["Draft: "])
        for i in draftUpdate:
            writer.writerow(i)


def fetchDataset(doi, forCodeTriplets):
    print("fetchDataset doi: " + doi + " triplets: " + str(forCodeTriplets))
    entries = (
        'id', 'versionNumber', 'versionMinorNumber', 'versionState', 'productionDate', 'lastUpdateTime', 'releaseTime',
        'createTime', 'UNF', 'files')
    try:
        r = requests.get(Constants.API_FETCHDATASET + doi, headers=Constants.API_DATAVERSES_GET_HEADER)
        print("fetch " + str(r.status_code))
        #print(json.loads(r.text))
        if r.status_code == 200 or r.status_code == 201:
            r.encoding = "utf-8"
            res = json.loads(r.text)
            if 'latestVersion' in res['data']:
                updateJSON = res['data']['latestVersion']
                status = res['data']['latestVersion']['versionState']
                print("fetchDataset versionStatus: ")
                print(status)
            else:
                logging(doi, 'unknown', "key latestVersion doesn't exist, the dataset could have been deaccessioned.")
                return
            for k in entries:
                updateJSON.pop(k, None)
            
            fields = editDataset(updateJSON, forCodeTriplets)
            updateJSON['metadataBlocks']['citation']['fields'] = fields
            
            updateDataset(doi, updateJSON, status)
        else:
            logging(doi, 'fetch', json.loads(r.text))
    except Exception as error:
        print('ERROR', error)


def editDataset(dataset, forCodeTriplets): #overwrites any topicClassifications already there
    print("editDataset()")
    fields = dataset['metadataBlocks']['citation']['fields']
    
    topicJSON = {}

    for dic in fields:
        for k,val in dic.items():
            if k == 'typeName' and val == 'topicClassification':
                print(f'{k} is {val}')
                topicJSON = dic

    if not topicJSON: #if topicJSON is null, there is no topicClassification sub-dict so create empty dict to add to
        topicJSON = {"typeName": "topicClassification",
                     "multiple": True,
                     "typeClass": "compound",
                     "value": [

                    ]
                    }

    print("topicJSON: ")
    print(topicJSON)

    for forCodeTriple in forCodeTriplets:   #expecting forCodeTriplets to be in form of "Term;vocab;vocabURI" - some will have only 1 triple, others 2 or more
        forCodeTripleArray = forCodeTriple.split(';')
        forCode = forCodeTripleArray[0].strip()
        forCodeVocab = forCodeTripleArray[1].strip()
        forCodeURI = forCodeTripleArray[2].strip()

        topicClass = {
                "topicClassValue": {
                  "typeName": "topicClassValue",
                  "multiple": False, #json.dumps should convert this to lowercase literal true
                  "typeClass": "primitive",
                  "value": forCode
                },
                "topicClassVocab": {
                  "typeName": "topicClassVocab",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": forCodeVocab
                },
                "topicClassVocabURI": {
                  "typeName": "topicClassVocabURI",
                  "multiple": False,
                  "typeClass": "primitive",
                  "value": forCodeURI
                }
        }
        topicJSON['value'].append(topicClass)

    for i in range(len(fields)):
        if fields[i]['typeName'] == 'topicClassification':
            fields[i] = topicJSON
            return fields

    print("not found") #no fields so len(fields) at line 160 is 0; code doesn't enter for loop at 160 so proceeds to this line
    fields.append(topicJSON)
    return fields


def logging(doi, stage, info):
    url = Constants.LOGGING_URL
    if stage == 'fetch':
        fetchError.append([doi, url + doi, info])
    elif stage == 'update':
        updateError.append([doi, url + doi, info])
    elif stage == 'publish':
        publishError.append([doi, url + doi, info])
    elif stage == 'draft':
        draftUpdate.append([doi, url + doi, info])
    elif stage == 'success':
        successDatasets.append([doi, url + doi])
    else:
        print("unknown error")
        unKnownError.append([doi, url + doi, info])

    print("Log saved.")


def updateDataset(doi, data, status):
    print("updateDataset()")

    try:
        tempD = json.dumps(data, ensure_ascii=True).encode('UTF-8')
    except Exception as error:
        print(error)
        logging(doi, 'unknown', error)
    try:
        r = requests.put(Constants.API_UPDATEDATASET + doi, data=tempD,
                         headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)

        print("update " + str(r.status_code))
        if r.status_code == 200 or r.status_code == 201:
            if status == 'RELEASED':
                publishDataset(doi)
            else:
                log = "Dataset is in draft mode, no need to publish."
                print(log)
                logging(doi, 'draft', log)

        else:
            print("Update failed !")
            logging(doi, 'update', json.loads(r.text))
    except Exception as error:
        print(error)
        logging(doi, 'unknown', error)


def publishDataset(doi):
    print("publishDataset()")

    try:
        r = requests.post(Constants.API_PUBLISHDATASET + doi + "&type=minor",
                          headers=Constants.API_DATAVERSES_PUBLISHDATASET_HEADER)
        print("publish " + str(r.status_code))
        if r.status_code == 200 or r.status_code == 201:
            print("Done")
            logging(doi, 'success', "")
        else:
            print("Publish failed !")
            logging(doi, 'publish', json.loads(r.text))
    except Exception as error:
        print('ERROR', error)


def main():
    print(str(currentDateTime()) + " Executing...")
    readCSV()
    


if __name__ == "__main__":
    main()