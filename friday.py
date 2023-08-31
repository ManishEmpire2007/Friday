from colorama import Fore, Style
import speech_recognition as sr
from gtts import gTTS
import webbrowser
import threading
import wikipedia
import tempfile
import requests
import datetime
import colorama
import pygame
import re
import io
import os

colorama.init(autoreset=True)

# response files (history)
response_folder = "history"
os.makedirs(response_folder, exist_ok=True)

#=== Math calculation
def calculate_response(text):
    calculation = re.sub(r'[^\w\s+\-*/%^]', '', text.replace("calculate", "").strip())
    calculation = calculation.replace("x", "*")
    calculation = calculation.replace("times", "*")
    calculation = calculation.replace("multiply", "*")
    try:
        result = eval(calculation)
        return f"The result of the calculation is: {result}"
    except Exception as e:
        return f"Sorry, I couldn't perform the calculation. Error: {str(e)}"

#=== Open website
def open_website_response(text):
    website_name = text.replace("open website", "").strip()
    website_urls = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
    }
    website_url = website_urls.get(website_name)
    if website_url:
        webbrowser.open(website_url)
        return f"Opening {website_name}..."
    else:
        return f"Sorry, I don't know how to open {website_name}."

#=== Wikipedia search
def wikipedia_search_response(query):
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return f"No Wikipedia results found for '{query}'."
        
        page_summary = wikipedia.summary(search_results[0], sentences=1)
        return f"Wikipedia summary: {page_summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        options = ', '.join(e.options[:5])
        return f"Disambiguation: Please specify your search with one of these options: {options}"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found for '{query}'."
    except Exception as e:
        return f"An error occurred while searching Wikipedia: {str(e)}"

#=== Main function
def recognize_audio(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio).lower()
        print(Fore.GREEN + "  You said:", text)
        #=== Commands and responses
        command_responses = {
            **{greeting: "Hello! How can I assist you today?" for greeting in ["hello", "hi", "hey"]},
            **{name: "I'm Friday. How can I help you today?" for name in ["your name", "who are you"]},
            **{taking_over: "I don't know, maybe in the near feature. hehe" for taking_over in ["takeover the world", "rule the world", "take over the world"]},
            **{credit: "Credits: This code was developed by Manish Aravindh from OMHSS. This voice-controlled assistant recognizes spoken commands, process them, and responds with synthesized speech. It utilizes the Google Web Speech A P I, the gTTS library." for credit in ["credits", "credit"]},
            **{intro: "Friday AI Voice Assistant is a project designed to demonstrate the power of voice controlled applications. This AI assistant can perform a variety of tasks simply by listening to your voice commands. From solving mathematical calculations to searching for information on the web, Friday is your virtual companion, ready to assist you with a wide range of tasks." for intro in ["intro", "about the project"]},
            **{calc: lambda: calculate_response(text) for calc in ["calculate", "calculator"]},
            "time": lambda: f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.",
            "wikipedia": lambda: wikipedia_search_response(text.replace("wikipedia", "").strip()),
            "open website": lambda: open_website_response(text),
            "exit": "Exiting now. Have a great day!",
        }

        response_text = None
        for command, response in command_responses.items():
            if command in text:
                if callable(response):
                    response_text = response()
                else:
                    response_text = response
                break
        if response_text is None:
            search_query = text
            response_text = f"Searching Google for {search_query}..."
            webbrowser.open(f"https://www.google.com/search?q={search_query}")

        print(Fore.GREEN + "  Response:", response_text)
        
        tts = gTTS(text=response_text, lang="en")
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        response_filename = os.path.join(response_folder, f"response_{timestamp}.mp3")
        tts.save(response_filename)

        pygame.mixer.init()
        pygame.mixer.music.load(response_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        if "exit" in text:
            return "exit"

    except sr.UnknownValueError:
        print(Fore.MAGENTA + "  An error occurred!")
    except sr.RequestError:
        print(Fore.MAGENTA + "  Sorry, there was an error connecting to the API.")

def main():
    recognizer = sr.Recognizer()
    while True:
        try:
            with sr.Microphone() as source:
                print(Fore.GREEN + Style.BRIGHT + "----- \nListening...")
                audio = recognizer.listen(source)
                recognized_text = recognize_audio(recognizer, audio)

                if recognized_text == "exit":
                    break
        except Exception as e:
            print(Fore.MAGENTA + f"  An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()

# =====