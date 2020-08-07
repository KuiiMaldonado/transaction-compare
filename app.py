#app.py script for making financial reconciliation and the flask app
#Developed by Cuitlahuac Daniel Maldonado Ruiz

#Import dependencies
import pandas as pd
from flask import Flask, render_template, request
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
def reconciliation(client_df, tutuka_df):

    #emptyDict stores in a dictionary all the column names of a dataframe as keys and empty values.
    #This variable helps out in the process of creating an empty row using the insertEmptyRow declared before.
    emptyDict = {}
    for column in client_df.columns:
        emptyDict[column] = ""

    print(emptyDict)

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
            else:
                #The ID's are not the same so we will check which ID is bigger. The biggest ID will have an empty row inserted before him.
                #With this method we ensure we check for same ID's even if they are in different dataframe index.

                if(clientRow["TransactionID"] > tutukaRow["TransactionID"]):
                    #If client id is bigger than tutuka ID it means we insert new row to client and the Tutuka ID doesn't have a match.
                    sortedClient = insertEmptyRow(sortedClient, index + 1, emptyDict)

                    #Each time we add a row to a dataframe we update the index to keep looping through all the dataframes rows
                    maxIndex = getMaxSize(sortedClient, sortedTutuka)
                    tutukaMismatch += 1
                    
                else:
                    #Viceversa tutuka ID is bigger than client ID it means we insert new row to tutuka and the client ID doesn't have a match.
                    sortedTutuka = insertEmptyRow(sortedTutuka, index + 1, emptyDict)

                    #Each time we add a row to a dataframe we update the index to keep looping through all the dataframes rows
                    maxIndex = getMaxSize(sortedClient, sortedTutuka)
                    clientMismatch += 1

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
        else:
            #Tutuka length is bigger than index so it has tutukaLen - index mismatched transactions to add.
            tutukaMismatch = tutukaMismatch + (tutukaLen - index)

        
    print(f'Client file matches: {clientMatch}')
    print(f'Client file possible: {clientPossible}')
    print(f'Client file Mismatches: {clientMismatch}')
    print(f'Tutuka file matches: {tutukaMatch}')
    print(f'Tutuka file possible: {tutukaPossible}')
    print(f'Tutuka file Mismatches: {tutukaMismatch}')

#Beginning of flask app
app = Flask(__name__)

@app.route("/home")
def home():
    return render_template("index.html")

@app.route("/uploader", methods = ["GET", "POST"])
def upload_files():
    if request.method == "POST":
        f1 = request.files["file1"]
        f2 = request.files["file2"]
        
        #Use index_col so pandas doesn't use the fisrt column as an index column.
        client_df = pd.read_csv(f1.stream, index_col=False)
        tutuka_df = pd.read_csv(f2.stream, index_col=False)
        reconciliation(client_df, tutuka_df)
        return "File uploaded successfully"

if __name__ == "__main__":
    app.run(debug=True)


