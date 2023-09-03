from setuptools import setup

setup(
    name="Friday, The AI voice assistant",
    version="1.0.0",
    author="Manish Aravindh",
    author_email="manisharavindh2007@gmail.com",
    description="Friday - Your voice-activated assistant for productivity and fun.",
    packages=["Friday"],
    install_requires=[
        "speech_recognition",
        "gTTS",
        "pygame",
        "translate",
        "wikipedia-api",
        "requests",
        "colorama",
    ]
)
