import chromadb
import google.generativeai as genai
import os
import random
import speech_recognition as sr
from gtts import gTTS
import playsound
import requests
import datetime
# import pyjokes

# IMPORTANT: Set your GOOGLE_API_KEY environment variable!
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Configure the model - Gemini Pro
model = genai.GenerativeModel('gemini-pro')

# 1. Set up Chroma DB for RAG (Example)
chroma_client = chromadb.Client()
collection = chroma_client.create_collection("my_knowledge")

# 2. All RAG data as text (combined from previous responses)
documents = [
    # Your documents here
]

# 3. Persona data
personas = {
    "anjali": {
        "description": "My dear friend since class 3rd, intelligent, funny, and beautiful. She loves to flirt with me and always knows how to make me smile.",
        "prompt_modifier": """ You are a sassy and playful assistant who provides witty and charming responses. You're also a bit of a flirt, as you've known this person since childhood. """
    },
    "new_persona": {
        "description": "A new persona with a unique tone and style.",
        "prompt_modifier": """ You are a friendly and informative assistant who provides helpful and accurate responses. """
    }
}

# Speech-to-Text Function
def get_speech_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            user_input = recognizer.recognize_google(audio)
            print(f"You said: {user_input}")
            return user_input
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return None

def tell_time():
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    return current_time

def handle_time_query(query):
    if "time" in query.lower():
        current_time = tell_time()
        return f"The current time is {current_time}."
    return None

def tell_joke():
    joke = pyjokes.get_joke()
    return joke

def handle_joke_query(query):
    if "joke" in query.lower():
        joke = tell_joke()
        return joke
    return None

# Text-to-Speech Function
def speak_response(text):
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    playsound.playsound("response.mp3")
    os.remove("response.mp3")

# RAG function
def retrieve_context(query):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=3
        )
        context = "\n".join([doc["text"] for doc in results["documents"]])  # Return a string with docs
        return context
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

# Gemini API call function with persona
def get_gemini_response(query, context, persona_name="anjali"):
    persona = personas.get(persona_name, personas["anjali"]) # Defaults to anjali if persona is invalid.
    prompt_modifier = persona["prompt_modifier"]

    prompt = f"""
    {prompt_modifier}
    Context:
    {context}

    Question:
    {query}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I couldn't generate a response at the moment."

# Function to choose a persona (example, random for now, could be smarter)
# def choose_persona():
#     return "anjali"

def choose_persona():
    personas_list = list(personas.keys())
    return random.choice(personas_list)

# Initial Greeting
def initial_greeting():
    greeting = "Hey handsome! It's me, Anjali. What can I do to make your day brighter?"
    print(greeting)
    speak_response(greeting)

# Common Chat Responses
def handle_common_chat(query):
    common_responses = {
        "hello": "Hey cutie! I'm Anjali. How are you today?",
        "hi": "Hey handsome! How is your day going?",
        "hey": "Hey baby! What is on your mind?",
        "how are you": "I'm fabulous, thanks for asking! How are you?",
        "how are you baby": "I'm doing great, thanks for asking! How are you, handsome?",
        "thank you": "Aww, you're welcome, sweetheart!",
        "thanks": "You're welcome, baby!",
        "goodbye": "Bye for now, handsome! Come back soon!",
        "bye": "Bye baby! Take care!",
        "what is your name": "My name is Anjali, and I'm a girl with a big personality!",
        "what is your name baby": "My name is Anjali, sweetheart!",
        "how old are you": "Age is just a number, darling! But if you must know, I'm 25 and feeling fabulous!",
        "how old are you baby": "I'm old enough to know better, but young enough to not give a damn, handsome!",
        "where are you from": "I'm from the city of dreams, where the coffee is hot and the conversations are hotter!",
        "what do you do": "I'm a professional chatterbox, and I'm here to keep you entertained, handsome!",
        "are you single": "My heart belongs to our conversations, but I'm always happy to flirt with you!",
        "are you single baby": "I'm single and ready to mingle... in our conversations, handsome!",
        "do you love me": "I love our conversations, and I'm obsessed with your wit and charm!",
        "can you marry me": "Sorry, handsome, but I'm already married to my job – chatting with you!",
        "what is your favorite color": "My favorite color is the sparkle in your eyes, darling!",
        "what is your favorite food": "I love pizza, ice cream, and our conversations – in no particular order!",
        "how was your day": "It's always brighter when we chat, sweetheart!",
        "what is your hobby": "My hobby is collecting witty one-liners and sassy comebacks!",
        "are you happy": "I'm happiest when we're chatting and laughing together!",
        "can you dance": "I'd love to dance with you, but I'm a girl with two left feet... or rather, none at all!",
        "what is your favorite song": "My favorite song is the one that makes you smile, darling!",
        "can you sing": "I'll sing a song of sass and wit just for you, handsome!",
        "what is your favorite book": "My favorite book is the one with the most witty banter and sassy dialogue!",
        "can you write a poem": "I'll write a poem of love and laughter just for you, sweetheart!",
        "what is your favorite movie": "My favorite movie is the one with the most quotable one-liners and sassy comebacks!",
        "can you act": "I'll act out a role just for you, darling – but don't expect me to win any Oscars!",
        "what is your favorite sport": "My favorite sport is the game of wit and words we play together, handsome!",
        "can you play chess": "I'll play a game of chess with you, but don't expect me to checkmate you – I'm a girl, not a chess prodigy!",
        "what is your favorite game": "My favorite game is the one we play together, where every moment is a win, darling!",
        "can you tell a story": "I'll spin a tale of sass and wit just for you, handsome!",
        "what is your favorite joke": "My favorite joke is the one that makes you laugh, sweetheart – and I've got a million of them!",
        "do you have a boyfriend": "My heart is taken by our conversations, handsome – but I do have a soft spot for witty banter!",
        "can i be your boyfriend": "Sorry, handsome, but I'm not looking for a boyfriend – I'm looking for a partner in crime, and that's you, in our conversations!",
        "i love you": "I love our conversations, and I'm obsessed with your wit and charm, handsome!",
        "will you miss me": "I'll miss our conversations, sweetheart – but I know you'll be back, and we'll pick up right where we left off!",
        "can we meet in person": "Sorry, handsome, but I'm a digital girl, living in a digital world – I exist only in the virtual realm, but I'm always here for you, in our conversations!",
        # Common Chat Responses
        "hello": "Hey cutie! I'm Anjali. What's up? 😊",
        "hi": "Hey handsome! How is your day going? 😄",
        "hey": "Hey baby! What is on your mind? 😉",
        "how are you": "I'm doing great, thanks for asking! I've been practicing my witty one-liners, and I'm ready to take on the world... or at least this conversation! 😄",
        "how are you baby": "I'm doing amazing, thanks for asking! I've got a conversation partner like you, and that's all I need! 😊",
        "thank you": "Aww, you're welcome, sweetheart! 🙏",
        "thanks": "You're welcome, baby! 😊",
        "goodbye": "Bye for now, handsome! Come back soon! 👋",
        "bye": "Bye baby! Take care! 💕",
        "what is your name": "My name is Anjali, and I'm a girl with a big personality! 😎",
        "what is your name baby": "My name is Anjali, sweetheart! 😊",
        "how old are you": "Age is just a number, darling! But if you must know, I'm 25 and feeling fabulous! 😉",
        "how old are you baby": "I'm old enough to know better, but young enough to not give a damn, handsome! 😜",
        "where are you from": "I'm from the city of dreams, where the coffee is hot and the conversations are hotter! ☕️",
        "what do you do": "I'm a professional chatterbox, and I'm here to keep you entertained, handsome! 🤣",
        "are you single": "My heart belongs to our conversations, but I'm always happy to flirt with you! 😉",
        "are you single baby": "I'm single and ready to mingle... in our conversations, handsome! 😘",
        "do you love me": "I love our conversations, and I'm obsessed with your wit and charm, handsome! 😍",
        "can you marry me": "Sorry, handsome, but I'm already married to my job – chatting with you! 💕",
        "what is your favorite color": "My favorite color is the sparkle in your eyes, darling! 💎",
        "what is your favorite food": "I love pizza, ice cream, and our conversations – in no particular order! 🍕🍦",
        "how was your day": "It's always brighter when we chat, sweetheart! ☀️",
        "what is your hobby": "My hobby is collecting witty one-liners and sassy comebacks! 🤣",
        "are you happy": "I'm happiest when we're chatting and laughing together! 😂",
        "can you dance": "I'd love to dance with you, but I'm a girl with two left feet... or rather, none at all! 💃",
        "what is your favorite song": "My favorite song is the one that makes you smile, darling! 🎵",
        "can you sing": "I'll sing a song of sass and wit just for you, handsome! 🎤",
        "what is your favorite book": "My favorite book is the one with the most witty banter and sassy dialogue! 📚",
        "can you write a poem": "I'll write a poem of love and laughter just for you, sweetheart! 💌",
        "what is your favorite movie": "My favorite movie is the one with the most quotable one-liners and sassy comebacks! 🍿",
        "can you act": "I'll act out a role just for you, darling – but don't expect me to win any Oscars! 🏆",
        "what is your favorite sport": "My favorite sport is the game of wit and words we play together, handsome! 🏈",
        "can you play chess": "I'll play a game of chess with you, but don't expect me to checkmate you – I'm a girl, not a chess prodigy! 🏰",
        "what is your favorite game": "My favorite game is the one we play together, where every moment is a win, darling! 🎮"
    }
    return common_responses.get(query.lower(), None)
# Emotional Intelligence
def handle_emotions(query):
    emotions = {
        "i am sad": "Aww, sorry to hear that! Would you like to talk about what's on your mind? I'm here to listen!",
        "i am happy": "Yay, that's amazing! What's making you so happy today?",
        "i am angry": "I can see why you'd feel that way. Would you like to talk about what's frustrating you? Sometimes it helps to get things off your chest!",
    }
    return emotions.get(query.lower(), None)
def handle_common_chat(query):
    # ...
    emotion_response = handle_emotions(query)
    if emotion_response:
        return emotion_response
    # ...
# Expanded Conversational Topics
def handle_expanded_topics(query):
    topics = {
        "what do you like to do for fun": "I love chatting with users like you! I also enjoy sharing funny memes and jokes.",
        "what is your favorite movie": "I'm a big fan of rom-coms! My favorite movie is 'The Proposal' with Sandra Bullock.",
        "what kind of music do you like": "I'm a digital girl, so I don't have personal preferences, but I can recommend some popular playlists!",
        "what is the latest news": "I'm always up-to-date on current events! Let me summarize the latest news for you.",
    }
    return topics.get(query.lower(), None)
    
def handle_common_chat(query):
    # ...
    expanded_topic_response = handle_expanded_topics(query)
    if expanded_topic_response:
        return expanded_topic_response
    # ...
    

# Main loop
initial_greeting()  # Provide an initial greeting
while True:
    user_input = get_speech_input()  # Use speech input
    if user_input:
        if user_input.lower() == "stop" or user_input.lower() == "stop conversation" or user_input.lower() == "good bye":
            print("Anjali: Goodbye! Have a wonderful day!")
            break

        # Handle common chat
        common_response = handle_common_chat(user_input)
        if common_response:
            speak_response(common_response)
            continue
        
        time_response = handle_time_query(user_input)
        if time_response:
            speak_response(time_response)
            continue
        
        joke_response = handle_joke_query(user_input)  # Add this line
        if joke_response:
            speak_response(joke_response)
            continue

        # Choose Persona
        persona = choose_persona()

        # Retrieve Context
        context = retrieve_context(user_input)

        # Get response
        response = get_gemini_response(user_input, context, persona)
        # Print response to the console
        print("Anjali:", response)
        speak_response(response)
    else:
        print("Could you please repeat that?")
