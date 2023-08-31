from colorama import Fore, Style
import colorama
import datetime
import io
import os
import re
import requests
import tempfile
import threading
import webbrowser
import pygame
import speech_recognition as sr
import wikipedia
from gtts import gTTS
from translate import Translator

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
        "spotify": "https://www.spotify.com",
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

#=== Translate function
def translate_text(text, recognizer, translation_occurred):
    if not translation_occurred:
        response_text = "Sure! Which language would you like to translate to?"
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
    
    text = text.replace("translate", "").strip()
            
    with sr.Microphone() as source:
        print(Fore.YELLOW + "\n  Listening for target language...")
        audio = recognizer.listen(source)
        target_language = recognizer.recognize_google(audio).lower()
        print(Fore.YELLOW + f"    Target language: {target_language}")

        target_languages = {
            "japanese": "ja",
            "tamil": "ta",
            "french": "fr",
            "german": "de",
            "spanish": "es",
        }

        if target_language in target_languages:
            target_language_code = target_languages[target_language]

            translator = Translator(to_lang=target_language_code)
            translated_text = translator.translate(text)

            print(Fore.YELLOW + f"    Translated ({target_language_code}): {translated_text}")

            translated_response = gTTS(text=translated_text, lang=target_language_code)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            translated_response_filename = os.path.join(response_folder, f"translated_response_{timestamp}.mp3")
            translated_response.save(translated_response_filename)

            pygame.mixer.init()
            pygame.mixer.music.load(translated_response_filename)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            print(Fore.YELLOW + f"    Translation to {target_language} is not supported.")
            return

#=== Spell a word
def spell_response(word):
    spelled_word = " ".join(word)
    return f"Sure! Here's how you spell '{word}': {spelled_word}"

#=== Define function to fetch word definitions
def fetch_word_definition(word):
    api_key = "b91d80395amsh67a5c63fe760c89p11a01fjsnd7dc41d4e88a"  # yeah, it is not working -_-!
    base_url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/definitions"

    headers = {
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com",
        "X-RapidAPI-Key": api_key
    }

    response = requests.get(base_url, headers=headers)
    data = response.json()

    if "definitions" in data:
        definitions = data["definitions"]
        if definitions:
            return definitions[0]["definition"]
        else:
            return f"No definitions found for '{word}'."
    else:
        return "An error occurred while fetching definitions."

#=== Main function
def recognize_audio(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio).lower()
        print(Fore.GREEN + "  You said:", text)

        translation_occurred = False
        #=== Commands and responses
        command_responses = {
            #=== fundamentals
            **{greeting: "Hello! How can I assist you today?" for greeting in ["hello", "hi", "hey"]},
            **{name: "I'm Friday. How can I help you today?" for name in ["your name", "who are you"]},
            **{taking_over: "I don't know, maybe in the near feature. hehe" for taking_over in ["takeover the world", "rule the world", "take over the world"]},
            **{credit: "Credits: This code was developed by Manish Aravindh from OMHSS. This voice-controlled assistant recognizes spoken commands, process them, and responds with synthesized speech. It utilizes the Google Web Speech A P I, the gTTS library." for credit in ["credits", "credit"]},
            **{intro: "Friday AI Voice Assistant is a project designed to demonstrate the power of voice controlled applications. This AI assistant can perform a variety of tasks simply by listening to your voice commands. From solving mathematical calculations to searching for information on the web, Friday is your virtual companion, ready to assist you with a wide range of tasks." for intro in ["intro", "about the project"]},
            **{exiting: "Exiting now. Have a great day!" for exiting in ["exit", "shutdown", "good bye"]},
            #=== functions
            "translate": lambda: translate_text(text, recognizer, translation_occurred),
            **{calc: lambda: calculate_response(text) for calc in ["calculate", "calculator"]},
            "wikipedia": lambda: wikipedia_search_response(text.replace("wikipedia", "").strip()),
            "time": lambda: f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.",
            "open website": lambda: open_website_response(text),
            "spell": lambda: spell_response(text.replace("spell", "").strip()),
            "play music": lambda: open_website_response("open website spotify"),
            "define": lambda: fetch_word_definition(text.replace("define", "").strip()),
            #=== more
            "tell me a fact": "Sure, here's a fact: Honey never spoils!",
            "tell me a story": "Once upon a time, in a land far, far away...",
            "joke": "Sure, I have a joke for you: Why don't scientists trust atoms? Because they make up everything! hehe",
            "riddle": "Here's a riddle for you: I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?",
            "meaning of life": "Ah, the age-old question. The meaning of life can vary from person to person, but it's often a journey of self-discovery and finding purpose.",
            #=== it can't (upcoming)
            "weather": "I'm sorry, I cannot provide real-time weather information at the moment.", #should open google weather
            "reminder": "I'm not equipped to set reminders at this time.",
            "news": "I'm sorry, I cannot provide current news updates.", #should open google news
            "email": "I don't have the capability to send emails.", #should open gmail or icloud
            "note": "I can't take notes, but you can try using a note-taking app like Evernote or Notion.",
            "set timer": "I can't set timers, but most devices have a built-in timer feature.",
            "set alarm": "I'm not able to set alarms, but your device likely has an alarm clock function.",
        }

        response_text = None
        for command, response in command_responses.items():
            if command in text:
                if callable(response):
                    response_text = response()
                    if command == "translate":
                        translation_occurred = True
                        response_text = "What else can I assist you with?"
                else:
                    response_text = response
                break
        if response_text is None and not translation_occurred:
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
                print(Fore.GREEN + Style.BRIGHT + "Listening... {")
                audio = recognizer.listen(source)
                recognized_text = recognize_audio(recognizer, audio)
                print(Fore.GREEN + Style.BRIGHT + "} ")

                if recognized_text == "exit":
                    break
        except Exception as e:
            print(Fore.MAGENTA + f"  An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()

#=== upcoming features
# correcting "define" and "spell"
# everything needed is already asked on ChatGPT
# more commands_responses
# more website links