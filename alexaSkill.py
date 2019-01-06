from __future__ import print_function
import json, urllib.request
import string


# ----------------------- 1. Response Functions -----------------------
def buildSpeechResponse(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "Bongo: " + title,
            'content': "Bongo: " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def buildResponse(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# ----------------------- 2. Custom User Messages -----------------------
def welcomeMessage():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Bongo! " \
                    "You can find bus times by saying, " \
                    "Alexa, ask Bongo for bus times."
    reprompt_text = "You can find bus times by saying, " \
                    "Alexa, ask Bongo for bus times."
    should_end_session = False
    return buildResponse(session_attributes, buildSpeechResponse(
        card_title, speech_output, reprompt_text, should_end_session))


def helpRequest():
    card_title = "Session Help"
    speech_output = "You're using the Bongo skill. You can ask me to tell you bus times by asking, Alexa, ask Bongo for bus times"
    should_end_session = False
    return buildResponse({}, buildSpeechResponse(
        card_title, speech_output, None, should_end_session))


def endRequest():
    card_title = "Session Ended"
    speech_output = "Session Ended"
    should_end_session = True
    return buildResponse({}, buildSpeechResponse(
        card_title, speech_output, None, should_end_session))


# ----------------------- 3. Intent Definitions -----------------------
def stopInfo(intent, session):
    card_title = intent['name']
    should_end_session = True

    # routeNameme?

    # routeProvided will be zero (false) if not provided, or one (true) if provided
    routeProvided = len(intent['slots']['routeNum']) - 1

    # Capture route, or assign default
    try:
        routeNum = intent['slots']['routeNum']['value']
    except:
        routeNum = "1050"

    requestString = "http://api.ebongo.org/prediction?stopid=" + routeNum + "&api_key=XXXX"
    with urllib.request.urlopen(requestString) as url:
        mainDict = json.loads(url.read().decode())

    predictionsList = mainDict["predictions"]
    print(predictionsList)

    # No Predictions Case
    if len(predictionsList) == 0:
        less30 = False
        speech_output = "There are no predictions availible for stop " + routeNum

    # Predictions availible
    else:
        less30 = True
        i = 0
        while less30:
            if predictionsList[i]["minutes"] <= 30:
                i = i + 1
            else:
                less30 = False

        busCountIn30 = i

        if busCountIn30 == 0:
            speech_output = "Theres no buses coming to stop number " + routeNum + " within the next 30 minutes."

        else:
            # If there's only one 1 bus vs multiple for proper grammar
            if busCountIn30 == 1:
                speech_output = "Theres " + str(
                    i) + " bus arriving at stop " + routeNum + " within the next 30 minutes. "
            else:
                speech_output = "There are " + str(
                    i) + " buses arriving at stop " + routeNum + " within the next 30 minutes. "

                # Individual Bus Info
            for j in range(0, busCountIn30):

                # Prefix assignments
                if j == 0 and busCountIn30 == 1:
                    prefix = "It's a "
                elif j == busCountIn30 - 1:
                    prefix = "and a "
                elif j != 0:
                    prefix + "a "
                elif j == 0:
                    prefix = "Theres a "

                # Assemble the bus string
                if predictionsList[j]['minutes'] == 0:
                    strMin = "any second now"
                else:
                    opS = "s"
                    if predictionsList[j]['minutes'] == 1:
                        opS = ""
                    strMin = "in " + str(predictionsList[j]['minutes']) + " minute" + opS

                busString = predictionsList[j]['title'] + " arriving " + strMin

                # Assemble all speech output
                speech_output = speech_output + prefix + busString

                # Punctuation
                if busCountIn30 != (j + 1):
                    speech_output = speech_output + ", "
                else:
                    speech_output = speech_output + "."

    print(speech_output)
    return buildResponse({}, buildSpeechResponse(card_title, speech_output, None, should_end_session))


# ----------------------- 4. Intent Caller -----------------------
def onIntent(request, session):
    # Session and request are the 2 JSON headers from the service simulator
    intent = request['intent']
    intentName = request['intent']['name']

    if intentName == "stopInfo":
        return stopInfo(intent, session)

    elif intentName == "EndSession":
        return endRequest()
    elif intentName == "HelpIntent":
        return helpRequest()
    elif intentName == "AMAZON.HelpIntent":
        return welcomeMessage()
    elif intentName == "AMAZON.CancelIntent" or intentName == "AMAZON.StopIntent":
        return endRequest()
    else:
        raise ValueError("Invalid intent")


# ----------------------- 5. Lambda Handler -----------------------
# Handler
def lambda_handler(event, context):
    if event['request']['type'] == "LaunchRequest":
        return welcomeMessage()

    elif event['request']['type'] == "IntentRequest":
        return onIntent(event['request'], event['session'])

    elif event['request']['type'] == "SessionEndedRequest":
        return endRequest()


'''
{
  "languageModel": {
    "intents": [
      {
        "name": "AMAZON.CancelIntent",
        "samples": []
      },
      {
        "name": "AMAZON.HelpIntent",
        "samples": []
      },
      {
        "name": "AMAZON.StopIntent",
        "samples": []
      },
      {
        "name": "stopInfo",
        "samples": [
          "when will the bus come to stop {routeNum}",
          "are there buses at stop {routeNum}",
          "How long till the bus is at {routeNum}",
          "How long till the bus is here",
          "if there's buses soon",
          "if there's buses soon at {routeNum}",
          "when the bus will get to {routeNum}",
          "when the bus will come",
          "if the bus is coming soon",
          "for bus times at stop {routeNum}",
          "for bus times",
          "to read me the bus times",
          "to read me the bus times at stop {routeNum}",
          "are there buses",
          "when will the buses come"
        ],
        "slots": [
          {
            "name": "routeNum",
            "type": "AMAZON.FOUR_DIGIT_NUMBER"
          }
        ]
      }
    ],
    "invocationName": "bongo"
  }
}
'''
