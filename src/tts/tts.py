import pyttsx3

def text_to_speech(text, output_file=None, voice_index=0):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print("\nAvailable voices:\n")
    for index, voice in enumerate(voices):
        print(f"{index}: {voice.name} - {voice.id}")

    if voice_index < len(voices):
        engine.setProperty('voice', voices[voice_index].id)
    else:
        print("[WARNING] Invalid voice index. Using default voice.")

    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

    if output_file:
        engine.save_to_file(text, output_file)
        engine.runAndWait()
        print(f"Audio saved to: {output_file}")
    else:
        engine.say(text)
        engine.runAndWait()
        print("Text spoken aloud.")

def test_text_to_speech_with_voice():
    text = "I am hungry"
    output_file = "test_output.wav"
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    print("\nAvailable voices:\n")
    for index, voice in enumerate(voices):
        print(f"{index}: {voice.name} - {voice.id}")

    try:
        selected_index = int(input("\nEnter the number of the voice you want to use: "))
        text_to_speech(text, output_file=None, voice_index= selected_index)
    except (ValueError, IndexError):
        print("Invalid input. Using default voice.")
        selected_index = 0

    

if __name__ == "__main__":
    test_text_to_speech_with_voice()
