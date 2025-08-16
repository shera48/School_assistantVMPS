import tkinter as tk
from tkinter import messagebox
import pyttsx3
import speech_recognition as sr
import threading
import time
from fuzzywuzzy import process
from datetime import datetime
import numpy as np
from PIL import Image, ImageTk
import webbrowser  

# ---------------- Core Logic ---------------- #
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

# Initialize TTS
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)

# Responses (trimmed for brevity)
responses = {
    "what is gravity": "Gravity is a force that attracts objects toward each other.",
    "who discovered electricity": "Benjamin Franklin is famous for his kite experiment in 1752.",
    "what is the time": lambda: f"The current time is {datetime.now().strftime('%H:%M')}",
    "who created you": "I was created by students of VMP School with the help of our AI teacher.",
    "what is your name": "I am your school query answering assistant."
}

normalized_responses = {k.lower(): v for k, v in responses.items()}

# ---------------- Functions ---------------- #
def animate_frequency():
    global is_animating, animation_id, phase
    if is_animating:
        canvas.delete("frequency_line")
        center_y = canvas.winfo_height() / 2
        spacing = canvas.winfo_width() / (num_lines + 1)
        for i in range(num_lines):
            x = spacing * (i + 1)
            offset = amplitude * np.sin(frequency * time.time() + i * 0.5 + phase)
            y1, y2 = center_y - offset, center_y + offset
            color = "#3498db" if i % 2 == 0 else "#2ecc71"
            canvas.create_line(x, y1, x, y2, width=line_width, fill=color, tags="frequency_line")
        phase += 0.3
        animation_id = root.after(50, animate_frequency)

def speak(text):
    text_box.config(state=tk.NORMAL)
    text_box.delete("1.0", tk.END)
    text_box.insert(tk.END, text)
    text_box.config(state=tk.DISABLED)
    root.update()
    tts_engine.say(text)
    tts_engine.runAndWait()

def search_google(query):
    if query:
        webbrowser.open(f"https://www.google.com/search?q={query}")

def find_best_match(query):
    best = process.extractOne(query, normalized_responses.keys())
    return best[0] if best and best[1] > 85 else None

def process_query():
    query = entry_question.get().strip().lower()
    button_google.pack_forget()
    best = find_best_match(query)
    if best:
        answer = normalized_responses[best]
        if callable(answer):
            answer = answer()
        speak(answer)
    else:
        speak("I don't know the answer to that.")
        button_google.pack(pady=5)

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        label_status.config(text="🎙️ Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            label_status.config(text="⏳ Processing...")
            query = recognizer.recognize_google(audio).lower()
            entry_question.delete(0, tk.END)
            entry_question.insert(0, query)
            process_query()
        except sr.UnknownValueError:
            label_status.config(text="⚠️ Couldn't understand.")
        except sr.RequestError:
            label_status.config(text="🚫 Speech service unavailable.")
        finally:
            stop_animation()

def start_listening(event):
    global is_animating
    is_animating = True
    animate_frequency()
    threading.Thread(target=recognize_speech).start()

def stop_animation():
    global is_animating, animation_id
    is_animating = False
    if animation_id:
        root.after_cancel(animation_id)
    canvas.delete("frequency_line")
    label_status.config(text="✅ Ready")

def stop_listening(event):
    stop_animation()

# ---------------- GUI ---------------- #
root = tk.Tk()
root.title("🎓 School Assistant")
root.geometry("1000x700")
root.config(bg="#ecf0f1")

# Background
try:
    bg_image = Image.open("school_background.png").resize((1000, 700))
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
except:
    pass

# Frame
frame = tk.Frame(root, bg="white", padx=20, pady=30, relief="raised", bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center")

label_title = tk.Label(frame, text="School Assistant 🤖", font=("Segoe UI", 20, "bold"), bg="white", fg="#2c3e50")
label_title.pack(pady=10)

label_question = tk.Label(frame, text="Ask me anything:", font=("Segoe UI", 12), bg="white")
label_question.pack()

entry_question = tk.Entry(frame, width=40, font=("Segoe UI", 14), relief="solid", bd=2)
entry_question.pack(pady=10)

button_ask = tk.Button(frame, text="🎤 Hold to Speak", font=("Segoe UI", 12, "bold"), bg="#3498db", fg="white", activebackground="#2980b9", relief="flat", padx=10, pady=5)
button_ask.pack(pady=10)
button_ask.bind("<ButtonPress-1>", start_listening)
button_ask.bind("<ButtonRelease-1>", stop_listening)

canvas = tk.Canvas(frame, width=200, height=90, bg="white", highlightthickness=0)
canvas.pack(pady=10)

label_status = tk.Label(frame, text="✅ Ready", font=("Segoe UI", 11), fg="green", bg="white")
label_status.pack()

text_box = tk.Text(frame, height=4, width=55, font=("Segoe UI", 12), wrap="word", state=tk.DISABLED, fg="#2c3e50", relief="solid", bd=2)
text_box.pack(pady=10)

button_submit = tk.Button(frame, text="💡 Submit Text", font=("Segoe UI", 12, "bold"), bg="#2ecc71", fg="white", activebackground="#27ae60", relief="flat", padx=10, pady=5, command=process_query)
button_submit.pack(pady=5)

button_google = tk.Button(frame, text="🌐 Search on Google", font=("Segoe UI", 12, "bold"), bg="#f39c12", fg="white", activebackground="#e67e22", relief="flat", padx=10, pady=5, command=lambda: search_google(entry_question.get()))
button_google.pack(pady=5)
button_google.pack_forget()

# Animation variables
is_animating = False
animation_id = None
num_lines = 6
line_width = 6
amplitude = 18
frequency = 0.2
phase = 0

root.mainloop()
