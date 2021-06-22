
# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import requests
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

from datetime import datetime, tzinfo, timedelta
import dateutil.parser
from dateutil.tz import gettz

query = {
   'key': #add your key here,
   'token': # add your token here
}

ZERO = timedelta(0)

class UTC(tzinfo):
    def utcoffset(self, dt):
        return ZERO
    def tzname(self, dt):
        return "UTC"
    def dst(self, dt):
        return ZERO

utc = UTC()

def getDuration(then, now = datetime.now(utc), interval = "default"):

    # Returns a duration as specified by variable interval
    # Functions, except totalDuration, returns [quotient, remainder]

    duration = now - then # For build-in functions
    duration_in_s = duration.total_seconds() 
    
    def years():
        return divmod(duration_in_s, 31536000) # Seconds in a year=31536000.

    def days(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 86400) # Seconds in a day = 86400

    def hours(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 3600) # Seconds in an hour = 3600

    def minutes(seconds = None):
        return divmod(seconds if seconds != None else duration_in_s, 60) # Seconds in a minute = 60

    def seconds(seconds = None):
        if seconds != None:
            return divmod(seconds, 1)   
        return duration_in_s

    def totalDuration():
        y = years()
        d = days(y[1]) # Use remainder to calculate next variable
        h = hours(d[1])
        m = minutes(h[1])
        
        # days = y*365 + d
        if(int(y[0])>0):
            return "{} years".format(int(y[0]))
        elif(int(d[0])>0):
            return "{} days".format(int(d[0]))
        elif(int(h[0])>0):
            return "{} hours".format(int(h[0]))
        else:
            return "{} minutes".format(int(m[0]))

    return {
        'years': int(years()[0]),
        'days': int(days()[0]),
        'hours': int(hours()[0]),
        'minutes': int(minutes()[0]),
        'seconds': int(seconds()),
        'default': totalDuration()
    }[interval]


def getCardMembers(cardID):
    url = f"https://api.trello.com/1/cards/<cardID>/members"
    response = requests.request(
      "GET",
      url,
      params=query
    )
    
    members = ""
    assigned_to = ""
    if(response.status_code == 200) :
        for member in json.loads(response.text):
            members += member.get("fullName") + ", "
        assigned_to = f"Assigned to {members}"
    else:
        assigned_to = f"Something went wrong. Status code: {response.status_code}. {response.text}"
    return assigned_to


def getCardsForList(listId, listName):
    speech = ""
    
    # Trello API begin
    url = f"https://api.trello.com/1/lists/{listId}/cards"
    cardsResponse = requests.request(
       "GET",
       url,
       params=query
    )
    # Trello API end
    
    if(cardsResponse.status_code == 200) :
        cards = json.loads(cardsResponse.text)
        s = ''
        are = "is"
        if (len(cards) > 1):
            s = 's'
            are = "are"
            speech += f"There {are} currently {len(cards)} task{s} in {listName}. "
        else:
            speech += "There are no tasks in {listName}"
            return speech
        
        if (len(cards) > 5):
            speech += "Here are the top 5. "
        else:
            speech += "They are. "
        
        for idx,card in enumerate(cards):
            if(idx == 5):
                break
            speech += "<voice name = 'Raveena'>" + f" {idx+1}, {card.get('name')} " + ".</voice>  "
            if (card.get("desc") != ""):
                speech += "<voice name = 'Matthew'>" + card.get("desc") + ".</voice> "
            if (len(card.get("idMembers")) < 1):
                speech += "<voice name = 'Emma'> Assigned to none</voice> "
            else:
                speech += "<voice name = 'Emma'> "+ getCardMembers(card.get('id')) +"</voice> "
                
            due = dateutil.parser.parse(card.get('due'))
            if(listName != "Backlog"):
                speech += "<voice name = 'Emma'> The deadline is in "+ getDuration(datetime.now(utc), now=due) +"</voice> "
            else:
                speech += "<voice name = 'Emma'> The deadline was "+ getDuration(due) +" ago. </voice>"
    else:
        speech = f"Something went wrong. Status code: {cardsResponse.status_code}. {cardsResponse.text}"
        
    print(speech)
    return speech


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Hi there. Welcome to the operations department. Here, you'll find all the relevant information from the operations department. You can ask me a query or say 'help' to know more."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class BriefIntentHandler(AbstractRequestHandler):
        
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("BriefIntent")(handler_input)

    def handle(self, handler_input):
        # Trello API begin
        boardId = "<Trello board id>"
        url = f"https://api.trello.com/1/boards/{boardId}/lists"
        responseLists = requests.request(
           "GET",
           url,
           params=query
        )
        # Trello api End
        
        speak_output = ""
        dayOrEvening = ""
        timezone = 'Australia/Sydney'
        py_timezone = gettz(timezone)
        currentTime = datetime.now(py_timezone)
        if currentTime.hour < 12:
            speak_output += "Good morning, Steve. "
            dayOrEvening = "Good day"
        elif 12 <= currentTime.hour < 18:
            speak_output += "Good afternoon, Steve. "
            dayOrEvening = "Good one"
        else:
            speak_output += "Good evening, Steve. "
            dayOrEvening = "Good evening"
            
        if(currentTime.hour > 12):
            speak_output += f"The time is {currentTime.hour - 12} {currentTime.minute} PM. "
        else:
            speak_output += f"The time is {currentTime.hour} {currentTime.minute} AM. "
        
        if(responseLists.status_code == 200) :
            for list in json.loads(responseLists.text):
                if(list.get("name") == "Done"):
                    continue
                else:
                    #speak_output += list.get('name')
                    speak_output += getCardsForList(list.get('id'), list.get('name'))
                    
            speak_output += f"That is the end. Have a {dayOrEvening}!"
        
        else:
            speak_output = f"Something went wrong. Status code: {responseLists.status_code}. {responseLists.text}"
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You are in help section. I am learning new skills to make it easy for you. Currently, I can help you with the latest status updates from the operations department. You can say, <voice name = 'Matthew'> 'get status updates from operations department' </voice> or say <voice name = 'Matthew'> 'ask operations department for a status update'</voice>. Hope that helps! "

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(BriefIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
