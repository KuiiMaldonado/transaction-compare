#app.py script for making financial reconciliation and the flask app
#Developed by Cuitlahuac Daniel Maldonado Ruiz

#Import dependencies
import pandas as pd
from flask import Flask, render_template, request, redirect, jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

#Beginning of the reconciliation script

## sortDataFrame - Sorts dataframe by column and ascending or descending order
# @params: dataframe - dataframe that will be sorted
#          column - name of column
#          ascending - True for ascending sort. False for descending sort.
# @return: sortedDF - the dataframe sorted
##
def sortDataFrame(dataframe, column, ascending):
    sortedDF = dataframe.sort_values(by=[column], ascending=ascending)

    #Reset the index of the dataframe
    sortedDF.index = [x for x in range(0, len(sortedDF))]
    return sortedDF

## insertEmptyRow - Inserts an empty row in a dataframe on the index defined.
# @params: dataframe - the dataframe in which the empty row will be inserted.
#          index - index where the row will be inserted. Index starts with number for first element of the dataframe.
# @return: df - dataframe with the new empty row inserted.
##
def insertEmptyRow(dataframe, index, emptyDict):
    row = pd.DataFrame(emptyDict, index=[index])
    df = pd.concat([dataframe.iloc[:index - 1], row, dataframe.iloc[index - 1:]], ignore_index=True)
    return df

## compareRowData - checks if the data of two rows is the same or not
# @params: clientRow - first pandas.Series to be compared
#          tutukaRow - pandas.Series which will be compared against.
# @return: Boolean
##
def compareRowData(clientRow, tutukaRow):
    flag = True
    for x in range(0,len(clientRow)):
        if(not (clientRow[x] == tutukaRow[x])):
            flag = False
            break
    return flag

## getMaxSize - return the len of the biggest dataframe
# @params: sortedClient - dataframe of the first csv file
#          sortedTutuka - dataframe of the second csv file      
# @return: length
##
def getMaxSize(sortedClient, sortedTutuka):
    #Get the length of both files so we can choose the largest file and iterate over that one
    clientLen = len(sortedClient)
    tutukaLen = len(sortedTutuka)

    #Assign the biggest length
    dfLen = clientLen if (clientLen > tutukaLen) else tutukaLen
    return dfLen

## reconciliation. The start point of data processing and reconciliation
# @params:  client_df - dataframe of the first file
#           tutuka_df - dataframe of the second file
#           f1_name - the name of the first file
#           f2_name - the name of the second file
# @return:   void
##
def reconciliation(client_df, tutuka_df, f1_name, f2_name):

    #emptyDict stores in a dictionary all the column names of a dataframe as keys and empty values.
    #This variable helps out in the process of creating an empty row using the insertEmptyRow declared before.
    emptyDict = {}
    for column in client_df.columns:
        emptyDict[column] = ""

    #Column names list to create the unmatched dataframe
    unmatchedColumns = ["FileName","TransactionID", "TransactionDate", "TransactionAmount", "TransactionNarrative"]

    #Column names list to create the possible dataframe
    possibleColumns = ["TransactionID", "TransactionDate", "TransactionAmount", "TransactionNarrative", 
                        "TransactionID_2", "TransactionDate_2", "TransactionAmount_2", "TransactionNarrative_2"]

    unmatched_df = pd.DataFrame(columns=unmatchedColumns)
    possible_df = pd.DataFrame(columns=possibleColumns)

    #Sort client dataframe by TransactionID (ascending order) so its easier to find possible matches.
    sortedClient = sortDataFrame(client_df, "TransactionID", True)

    #Sort tutuka dataframe by TransactionID (ascending order)
    sortedTutuka = sortDataFrame(tutuka_df, "TransactionID", True)

    #We look through each dataframe and search if there are transactions that are the same.
    #If we find the same transaction in the same dataframe. We drop it.
    #Because is a transaction that is repeated and will cause problems. i.e. calculating the correct total amount the client
    #or a reatil store really  sold.

    #Drop duplicates in sortedClient dataframe
    sortedClient.drop_duplicates(inplace=True)
    #Reset the index of the dataframe
    sortedClient.index = [x for x in range(0, len(sortedClient))]

    #Drop duplicates in sortedTutuka dataframe
    sortedTutuka.drop_duplicates(inplace=True)
    #Reset the index of the dataframe
    sortedTutuka.index = [x for x in range(0, len(sortedTutuka))]

    #Fill blanks cells (if exist) with
    sortedClient.fillna(value=0, axis=1, inplace=True)
    sortedTutuka.fillna(value=0, axis=1, inplace=True)

    # We start the iteration through the dataframes comparing each index within both dataframes. This is possible because we have sorted the data
    # And We dropped duplicates too
    index = 0
    clientMatch = 0
    clientMismatch = 0
    clientPossible = 0
    tutukaMatch = 0
    tutukaMismatch = 0
    tutukaPossible = 0
    #We use the biggest dataframe size to iterate in the while loop
    maxIndex = getMaxSize(sortedClient, sortedTutuka)

    while(index < maxIndex):
        try:
            clientRow = sortedClient.iloc[index]
            tutukaRow = sortedTutuka.iloc[index]
            
            #First only check if the TransactionsID are the same. If both match, continue to check all the other data.
            if(clientRow["TransactionID"] == tutukaRow["TransactionID"]):
                if(compareRowData(clientRow, tutukaRow)): 
                    #Add one match to each file because the transaction is on both. So is a perfect match for both of them
                    clientMatch += 1
                    tutukaMatch += 1
                else:
                    #If they have the same ID but different information it may be possible that script has switched the transactionDescription in one file.
                    #But the transaction may still have a match
                    #So we check with the next row if we find the same description.

                    tutukaNextRow = sortedTutuka.iloc[index + 1]
                    clientNextRow = sortedClient.iloc[index + 1]
                    if(compareRowData(clientRow, tutukaNextRow)):
                        
                        #Add new matches
                        clientMatch += 1
                        tutukaMatch += 1
                        if(compareRowData(clientNextRow, tutukaRow)):
                            clientMatch += 1
                            tutukaMatch += 1
                        else:
                            clientMismatch += 1
                            tutukaMismatch += 1
                        #Add one to index because we already checked the next row
                        index += 1
                    else:
                        #Here it means transactions have the same ID but have at least one column different so they are a possible match.
                        clientPossible += 1
                        tutukaPossible += 1

                        #We add the possible match to the possible_df
                        possible_df = possible_df.append({"TransactionID":clientRow["TransactionID"], "TransactionDate":clientRow["TransactionDate"],
                                                        "TransactionAmount":clientRow["TransactionAmount"], "TransactionNarrative":clientRow["TransactionNarrative"],
                                                        "TransactionID_2":tutukaRow["TransactionID"], "TransactionDate_2":tutukaRow["TransactionDate"],
                                                        "TransactionAmount_2":tutukaRow["TransactionAmount"], "TransactionNarrative_2":tutukaRow["TransactionNarrative"]}, ignore_index=True)              
            else:
                #The ID's are not the same so we will check which ID is bigger. The biggest ID will have an empty row inserted before him.
                #With this method we ensure we check for same ID's even if they are in different dataframe index.

                if(clientRow["TransactionID"] > tutukaRow["TransactionID"]):
                    #If client id is bigger than tutuka ID it means we insert new row to client and the Tutuka ID doesn't have a match.
                    sortedClient = insertEmptyRow(sortedClient, index + 1, emptyDict)

                    #Each time we add a row to a dataframe we update the index to keep looping through all the dataframes rows
                    maxIndex = getMaxSize(sortedClient, sortedTutuka)
                    tutukaMismatch += 1

                    #We add the mismatch to the unmatched_df
                    unmatched_df = unmatched_df.append({"FileName":f2_name, "TransactionID":tutukaRow["TransactionID"], "TransactionDate":tutukaRow["TransactionDate"],
                                                        "TransactionAmount":tutukaRow["TransactionAmount"], "TransactionNarrative":tutukaRow["TransactionNarrative"]}, ignore_index=True)
                    
                else:
                    #Viceversa tutuka ID is bigger than client ID it means we insert new row to tutuka and the client ID doesn't have a match.
                    sortedTutuka = insertEmptyRow(sortedTutuka, index + 1, emptyDict)

                    #Each time we add a row to a dataframe we update the index to keep looping through all the dataframes rows
                    maxIndex = getMaxSize(sortedClient, sortedTutuka)
                    clientMismatch += 1

                    #We add the mismatch to the unmatched_df
                    unmatched_df = unmatched_df.append({"FileName":f1_name, "TransactionID":clientRow["TransactionID"], "TransactionDate":clientRow["TransactionDate"],
                                                        "TransactionAmount":clientRow["TransactionAmount"], "TransactionNarrative":clientRow["TransactionNarrative"]}, ignore_index=True)

            index += 1
        except (IndexError):
            #Catching this exception means one dataframe has more rows than the other one. We have reached the end of one dataframe.
            #Break the loop
            break

    #After exiting the loop we check until which index we reached. And if a dataframe length is bigger than the last index we check.
    #It means that dataframe has more transactions that don't have a match.

    clientLen = len(sortedClient)
    tutukaLen = len(sortedTutuka)

    if(index < maxIndex):
        if(clientLen > index):
            #Client length is bigger than index so it has clientLen - index mismatched transactions to add.
            clientMismatch = clientMismatch + (clientLen - index)
            while(index < maxIndex):
                clientRow = sortedClient.iloc[index]

                #We add the mismatch to the unmatched_df
                unmatched_df = unmatched_df.append({"FileName":f1_name, "TransactionID":clientRow["TransactionID"], "TransactionDate":clientRow["TransactionDate"],
                                                        "TransactionAmount":clientRow["TransactionAmount"], "TransactionNarrative":clientRow["TransactionNarrative"]}, ignore_index=True)
                index += 1
        else:
            #Tutuka length is bigger than index so it has tutukaLen - index mismatched transactions to add.
            tutukaMismatch = tutukaMismatch + (tutukaLen - index)
            while(index < maxIndex):
                tutukaRow = sortedTutuka.iloc[index]

                #We add the mismatch to the unmatched_df
                unmatched_df = unmatched_df.append({"FileName":f1_name, "TransactionID":clientRow["TransactionID"], "TransactionDate":clientRow["TransactionDate"],
                                                        "TransactionAmount":clientRow["TransactionAmount"], "TransactionNarrative":clientRow["TransactionNarrative"]}, ignore_index=True)
                index += 1

    #Update the data in the dictionary reconData to update it in the webpage
    reconData = {'file1':{'name':"", "total":0, "matches":0, "possible":0, "mismatches":0},
                'file2':{'name':"", "total":0, "matches":0, "possible":0, "mismatches":0}}

    #Adding file 1 data to the dictionary
    reconData["file1"]["name"] = f1_name
    reconData["file1"]["total"] = clientMatch + clientPossible + clientMismatch
    reconData["file1"]["matches"] = clientMatch
    reconData["file1"]["possible"] = clientPossible
    reconData["file1"]["mismatches"] = clientMismatch
    #Adding file 2 data to the dictionary
    reconData["file2"]["name"] = f2_name
    reconData["file2"]["total"] = tutukaMatch + tutukaPossible + tutukaMismatch
    reconData["file2"]["matches"] = tutukaMatch
    reconData["file2"]["possible"] = tutukaPossible
    reconData["file2"]["mismatches"] = tutukaMismatch

    #Parsing the dataframes as dictionaries and save them in the response dictionary.
    reconData["unmatched"] = unmatched_df.to_dict("index")
    reconData["possible"] = possible_df.to_dict("index")

    #Return the data dictionary
    return reconData


#Beginning of flask app
app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route("/")
@cross_origin(supports_credentials=True)
def index():
    #render the index.html
    return render_template("index.html")

@app.route("/reconciliation", methods = ["GET", "POST"])
@cross_origin(supports_credentials=True)
def processing():
    if request.method == "POST":
        #Get the uploaded files
        f1 = request.files["file1"]
        f2 = request.files["file2"]
        
        #Get the dataframe for each uploaded file.
        # Use index_col so pandas doesn't use the fisrt column as an index column.
        client_df = pd.read_csv(f1.stream, index_col=False)
        tutuka_df = pd.read_csv(f2.stream, index_col=False)

        reconData = reconciliation(client_df, tutuka_df, f1.filename, f2.filename)
        #jsonify the data and git it as response
        return jsonify(reconData)

if __name__ == "__main__":
    app.run(debug=True)


