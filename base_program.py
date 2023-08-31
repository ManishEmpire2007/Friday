import speech_recognition as sr
from gtts import gTTS
import pygame
import threading
import tempfile
import requests
import wikipedia
import webbrowser
import datetime
import re
import io
import os
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

# response files (history)
response_folder = "history"
os.makedirs(response_folder, exist_ok=True)

def recognize_audio(recognizer, audio):
    try:
        # Recognize the audio using Google Web Speech API
        text = recognizer.recognize_google(audio).lower()
        print(Fore.GREEN + "  You said:", text)
        
        #===== Commands and responses
        greetings = ["hello", "hi", "hey"]
        Credits = ["credits", "credit"]
        if "your name" in text:
            response_text = "My name is Friday! How can I assist you today?"
        elif any(Credit in text for Credit in Credits):
            response_text = "Credits: This code was developed by Manish Aravindh from OMHSS. This voice-controlled assistant recognizes spoken commands, process them, and responds with synthesized speech. It utilizes the Google Web Speech A P I, the gTTS library."
        elif "hello" in text:
            response_text = "Hello! How can I assist you today?"
        elif "time" in text:
            current_time = datetime.datetime.now().strftime("%H:%M")
            response_text = f"The current time is {current_time}."
        elif "exit" in text:
            response_text = "Exiting now. Have a great day!"
        #===== Math calculation
        elif "calculate" in text:
            calculation = re.sub(r'[^\w\s+\-*/%^]', '', text.replace("calculate", "").strip())
            calculation = calculation.replace("x", "*")
            try:
                result = eval(calculation)
                response_text = f"The result of the calculation is: {result}" 
            except Exception as e:
                response_text = f"Sorry, I couldn't perform the calculation. Error: {str(e)}"
        #===== Google search
        elif "google" in text:
            search_query = text.replace("google", "").strip()
            response_text = f"Opening Google search for {search_query}..."
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        #===== Wikipedia search
        elif "wikipedia" in text:
            search_query = text.replace("wikipedia", "").strip()
            try:
                search_result = wikipedia.summary(search_query, sentences=2)
                response_text = f"Here is a summary from Wikipedia: {search_result}"
            except wikipedia.DisambiguationError as e:
                response_text = "There are multiple possible matches. Please be more specific."
            except wikipedia.PageError:
                response_text = "Sorry, I couldn't find information on that topic."
        else:
            # response_text = "Sorry, I didn't understand that command."
            search_query = text
            response_text = f"Opening Google search for {search_query}..."
            webbrowser.open(f"https://www.google.com/search?q={search_query}")

        print(Fore.GREEN + "  Response:", response_text)
    
        # Convert response to speech
        tts = gTTS(text=response_text, lang="en")
        
        # Save response to history
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        response_filename = os.path.join(response_folder, f"response_{timestamp}.mp3")
        tts.save(response_filename)

        # Play the response
        pygame.mixer.init()
        pygame.mixer.music.load(response_filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except sr.UnknownValueError:
        print(Fore.MAGENTA + "  An error occurred!")
    except sr.RequestError:
        print(Fore.MAGENTA + "  Sorry, there was an error connecting to the API.")

def main():
    # Create a recognizer instance
    recognizer = sr.Recognizer()

    while True:
        # Capture audio from the microphone
        with sr.Microphone() as source:
            print(Fore.GREEN + Style.BRIGHT + "----- \nListening...")
            audio = recognizer.listen(source)
            recognize_audio(recognizer, audio)

            # Exiting...
            if "exit" in recognizer.recognize_google(audio).lower():
                    break

if __name__ == "__main__":
    main()
