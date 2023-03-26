import feedparser
import requests
from pydub import AudioSegment
from speech_recognition import Recognizer, AudioFile
from io import BytesIO
import openai

# Replace with the RSS feed URL you want to process
rss_feed_url = "https://example.com/rss_feed.xml"

# Replace with your GPT-4 API key
gpt4_api_key = "your_api_key_here"

# Initialize GPT-4 API
openai.api_key = gpt4_api_key

# Read the RSS feed
feed = feedparser.parse(rss_feed_url)

# Extract the first audio file from the feed
first_audio_url = None
for entry in feed.entries:
    for link in entry.links:
        if link.type.startswith("audio"):
            first_audio_url = link.href
            break
    if first_audio_url:
        break

if not first_audio_url:
    print("No audio file found in the RSS feed.")
    exit()

# Download the audio file
response = requests.get(first_audio_url)
audio_data = BytesIO(response.content)

# Load and transcribe the audio file
audio = AudioSegment.from_file(audio_data)
recognizer = Recognizer()

with BytesIO() as audio_file:
    audio.export(audio_file, format="wav")
    audio_file.seek(0)

    with AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)

transcript = recognizer.recognize_google(audio_data)

print("Transcript:", transcript)

# Feed the transcript to GPT-4
gpt4_response = openai.Completion.create(
    engine="gpt-4",
    prompt=f"Learn from the following podcast transcript:\n{transcript}\n\n",
    max_tokens=50,
    n=1,
    stop=None,
    temperature=0.5,
)

print("GPT-4 response:", gpt4_response.choices[0].text.strip())
