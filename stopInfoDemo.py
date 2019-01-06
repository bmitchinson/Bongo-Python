import json, urllib.request
import string

def routeListing():
    with urllib.request.urlopen("http://api.ebongo.org/routelist?format=json&api_key=XXXX") as url:
            mainDict = json.loads(url.read().decode())

    mainList = mainDict['routes']

    for routeDict in mainList:
        routeInfoDict = routeDict["route"]
        print("ID: ",routeInfoDict["id"])

def predictions(stop = 1015):
    stopID = stop
    print("Searching for " + str(stopID))
    requestString = "http://api.ebongo.org/prediction?stopid=" + str(stopID) + "&api_key=XXXX"
    with urllib.request.urlopen(requestString) as url:
            mainDict = json.loads(url.read().decode())

    predictionsList = mainDict["predictions"]
    #print(predictionsList)
    
    if predictionsList == []:
        print("No predictions for stop " + str(stopID) +"."
              +" Busses must not be running right now.")

    else:
        less30 = True
        #i representing the amount of busses within 30 mintues
        i = 0

        while less30:
            if predictionsList[i]["minutes"] > 30:
                less30 = False
            else:
                print("Theres a",predictionsList[i]['title'],"in",predictionsList[i]['minutes'],"coming to stop ",stopID)
                i = i + 1

def main():
    stop = int(input("Please Enter Stop ID: "))  #1015 is currier bus stop near burge
    predictions(stop)
    
if __name__ == "__main__":
    main()
