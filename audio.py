import speech_recognition as sr
import os
import pandas as pd

r = sr.Recognizer()
data = []

base_path = r"D:/Voice chatbot/bank_audio"

for intent in os.listdir(base_path):
    intent_path = os.path.join(base_path, intent)

    if not os.path.isdir(intent_path):
        continue

    for file in os.listdir(intent_path):
        if file.lower().endswith(".wav"):
            file_path = os.path.join(intent_path, file)

            try:
                with sr.AudioFile(file_path) as source:
                    audio = r.record(source)

                text = r.recognize_google(audio)
                print(file, ":", text)

                data.append([text.lower(), intent])

            except Exception as e:
                print("Error in", file, "|", e)

df = pd.DataFrame(data, columns=["text", "intent"])
df.to_csv("bank_chatbot_dataset.csv", index=False)

print(df)
print("Dataset created successfully")
