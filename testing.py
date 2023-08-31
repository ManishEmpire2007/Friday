import colorama
from colorama import Fore, Style
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
import random

# Initialize colorama for colored output
colorama.init(autoreset=True)

#=== response files (history)
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
        return f"I'm sorry, I couldn't perform the calculation. Error: {str(e)}"

#=== Open website
def open_website_response(text):
    website_name = text.replace("open website", "").strip()
    website_urls = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "spotify": "https://www.spotify.com",
        "gmail": "https://mail.google.com",
        "news": "https://news.google.com",
        "keep": "https://keep.google.com",
        "weather": "https://weather.com",
    }
    website_url = website_urls.get(website_name)
    if website_url:
        webbrowser.open(website_url)
        return f"Sure, I'm opening {website_name} for you..."
    else:
        return f"I apologize, but I don't know how to open {website_name}."

#=== Wikipedia search
def wikipedia_search_response(query):
    try:
        search_results = wikipedia.search(query)
        if not search_results:
            return f"I couldn't find any Wikipedia results for '{query}'."
        
        page_summary = wikipedia.summary(search_results[0], sentences=1)
        return f"Here's a summary from Wikipedia: {page_summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        options = ', '.join(e.options[:5])
        return f"There are multiple options for '{query}'. Please specify one: {options}"
    except wikipedia.exceptions.PageError:
        return f"I couldn't find a Wikipedia page for '{query}'."
    except Exception as e:
        return f"An error occurred while searching Wikipedia: {str(e)}"

#=== Translate function
def translate_text(text, recognizer, translation_occurred):
    if not translation_occurred:
        response_text = "Of course! Which language would you like to translate to?"
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

#=== Get time
def get_time_of_day():
    current_hour = datetime.datetime.now().hour
    if 6 <= current_hour < 12:
        return "Good morning!"
    elif 12 <= current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

#=== Main function to recognize audio
def recognize_audio(recognizer, audio):
    try:
        text = recognizer.recognize_google(audio).lower()
        print(Fore.GREEN + "  You said:", text)
        jokes = [
            "Alright, here's a joke for you: Why don't scientists trust atoms? Because they make up everything!",
            "Here's one: Why did the scarecrow win an award? Because he was outstanding in his field!",
            "How about this: Why don't oysters donate to charity? Because they're shellfish!",
            "Here's a classic: Did you hear about the mathematician who’s afraid of negative numbers? He’ll stop at nothing to avoid them!",
            "Here's a thinker: Why was the math book sad? Because it had too many problems.",
            "A little music humor: I used to play piano by ear, but now I use my hands.",
            "And here's a geometry gem: Parallel lines have so much in common. It’s a shame they’ll never meet.",
        ]
        riddles = [
            "Alright, here's a riddle for you: What has keys but can't open locks?",  # A piano
            "How about this: I've got cities, but no houses. Forests, but no trees. Water, but no fish. What am I?",  # A map
            "Here's a thinker: The more you take, the more you leave behind. What am I?",  # Footsteps
            "Ever heard this one? What can travel around the world while staying in a corner?",  # A postage stamp
            "Here's a puzzler: I've got a heart that doesn't beat. A home, but no life. What am I?",  # An artichoke
            "Check this out: What has a face that never frowns, a bed but never sleeps, and runs but never walks?",  # A clock
            "Here's an enigma for you: The more you look at it, the less you see. What is it?"  # Darkness
        ]
        facts = [
            "Did you know? Honey never spoils, thanks to its low moisture and acidic pH.",
            "Fascinating fact: Octopuses have three hearts: two pump blood to the gills, and one circulates it to the rest of the body.",
            "Here's an interesting tidbit: The Great Wall of China isn't visible from space without aid, contrary to popular belief.",
            "Mind-blowing fact: The Eiffel Tower can grow about 6 inches in height during the hot summer due to metal expansion.",
            "Did you know? Bananas are berries, but strawberries aren't. Botanical definitions can be surprising!",
            "Curious fact: The shortest war ever recorded lasted just 38 minutes between Britain and Zanzibar in 1896.",
            "Fun fact: The world's oldest known recipe is for beer, hailing from ancient Mesopotamia. Cheers to history!"
        ]
        life = [
            "Life is like a box of chocolates, you never know what you're gonna get.",
            "Ah, the age-old question. The meaning of life can vary from person to person, but it's often a journey of self-discovery and finding purpose.",
            "The meaning of life might be about creating meaningful connections and relationships with others.",
            "Some say that the purpose of life is to seek happiness and make the most out of every moment.",
            "The meaning of life could simply be to experience the journey, embrace challenges, and learn from every step.",
            "Ultimately, the answer to the meaning of life is a deeply personal and philosophical question that each individual must explore for themselves."
        ]
        translation_occurred = False
        
        # Command-response dictionary
        command_responses = {
            **{greeting: "Hello! How can I assist you today?" for greeting in ["hello", "hi", "hey"]},
            **{name: "I'm Friday. How can I help you today?" for name in ["your name", "who are you"]},
            **{credit: "Credits: This code was developed by Manish Aravindh from OMHSS. This voice-controlled assistant recognizes spoken commands, processes them, and responds with synthesized speech. It utilizes the Google Web Speech API and the gTTS library." for credit in ["credits", "credit"]},
            **{taking_over: "I don't know, maybe in the near future. Hehe" for taking_over in ["takeover the world", "rule the world", "take over the world"]},
            **{intro: "Friday AI Voice Assistant is a project designed to demonstrate the power of voice-controlled applications. This AI assistant can perform a variety of tasks simply by listening to your voice commands. From solving mathematical calculations to searching for information on the web, Friday is your virtual companion, ready to assist you with a wide range of tasks." for intro in ["intro", "about the project"]},
            **{exiting: "Exiting now. Have a great day!" for exiting in ["exit", "shutdown", "goodbye"]},
            #=== Functions
            **{goods: lambda: f"{get_time_of_day()} How can I assist you today?" for goods in ["good morning", "good afternoon", "good evening"]},
            **{calc: lambda: calculate_response(text) for calc in ["calculate", "calculator"]},
            "wikipedia": lambda: wikipedia_search_response(text.replace("wikipedia", "").strip()),
            "time": lambda: f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}.",
            "translate": lambda: translate_text(text, recognizer, translation_occurred),
            "spell": lambda: spell_response(text.replace("spell", "").strip()),
            "open website": lambda: open_website_response(text),
            #=== More
            "joke": lambda: random.choice(jokes),
            "fact": lambda: random.choice(facts),
            "riddle": lambda: random.choice(riddles),
            "meaning of life": lambda: random.choice(life),
            "play music": lambda: open_website_response("open website spotify"),
            "email": lambda: open_website_response("open website gmail"),
            "news": lambda: open_website_response("open website news"),
            "weather": lambda: open_website_response("open website weather"),
            "notes": lambda: open_website_response("open website keep"),
            #=== Unsupported commands
            "reminder": "I'm not equipped to set reminders at this time.",
            "note": "I can't take notes, but you can try using a note-taking app like Evernote or Notion.",
            "set timer": "I can't set timers, but your devices have a built-in timer feature.",
            "set alarm": "I'm not able to set alarms, but your device likely has an alarm clock function.",
            "define": "I'm not equipped to provide definitions, but you can use online dictionaries like Merriam-Webster or Oxford.",
            #=== New commands
            "date": lambda: f"Today's is {datetime.datetime.now().strftime('%B %d, %Y')}.",
            # "day": lambda: f"Today's is {daytime.daytime.now().strftime('%B %d, %Y')}.",
            "how are you": "I'm just a computer program, but I appreciate you asking!",
            "thanks": "You're welcome! If you have more questions, feel free to ask.",
        }

        response_text = None
        for command, response in command_responses.items():
            if command in text:
                if callable(response):
                    response_text = response()
                    if command == "translate":
                        translation_occurred = True
                        response_text = "Is there anything else I can help you with?"
                else:
                    response_text = response
                break
        if response_text is None and not translation_occurred:
            search_query = text
            response_text = f"Searching Google for '{search_query}'..."
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
            pygame.time.Clock().tick(100)

        if "exit" in text:
            return "exit"

    except sr.UnknownValueError:
        print(Fore.MAGENTA + "  An error occurred while trying to understand your speech.")
    except sr.RequestError:
        print(Fore.MAGENTA + "  I'm sorry, there was an error connecting to the speech recognition service.")

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

#=== Upcoming features
# improving command and response so that they will not one and other ***
# Adding more website links for easier access
# Implementing additional functionalities as needed
