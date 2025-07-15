import tkinter as tk
from tkinter import messagebox
import openai
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
WP_URL = os.getenv("WP_URL")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

def generate_article():
    topic = topic_entry.get()
    keywords = keywords_entry.get()
    if not topic or not keywords:
        messagebox.showerror("Input Error", "Please enter both topic and keywords.")
        return

    prompt = f"""
    Write a 600-word blog post targeted at Hong Kong parents searching for Primary 5 English tutoring.
    Include an SEO-optimized title, meta description (max 160 characters), and at least three subheadings.
    Use a clear and friendly tone and include these keywords: {keywords}.
    Topic: {topic}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        content = response['choices'][0]['message']['content']
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, content)
    except Exception as e:
        messagebox.showerror("API Error", str(e))

def post_to_wordpress():
    content = text_output.get("1.0", tk.END).strip()
    if not content:
        messagebox.showerror("Content Error", "No content to publish.")
        return

    # Extract title from content (first line)
    lines = content.split("\n")
    title = lines[0] if lines else "Untitled Post"

    try:
        response = requests.post(
            f"{WP_URL}/wp-json/wp/v2/posts",
            auth=(WP_USERNAME, WP_PASSWORD),
            headers={'Content-Type': 'application/json'},
            json={
                "title": title,
                "content": content,
                "status": "draft"  # Change to "publish" to go live immediately
            }
        )
        if response.status_code == 201:
            messagebox.showinfo("Success", "Article posted to WordPress as draft.")
        else:
            messagebox.showerror("Post Error", response.text)
    except Exception as e:
        messagebox.showerror("Request Error", str(e))

# GUI setup
root = tk.Tk()
root.title("補習社自動產文助手")

tk.Label(root, text="主題:").grid(row=0, column=0, sticky="e")
topic_entry = tk.Entry(root, width=50)
topic_entry.grid(row=0, column=1)

tk.Label(root, text="關鍵字:").grid(row=1, column=0, sticky="e")
keywords_entry = tk.Entry(root, width=50)
keywords_entry.grid(row=1, column=1)

tk.Button(root, text="產生文章", command=generate_article).grid(row=2, column=0, columnspan=2, pady=10)
tk.Button(root, text="發佈到 WordPress", command=post_to_wordpress).grid(row=3, column=0, columnspan=2, pady=5)

text_output = tk.Text(root, wrap=tk.WORD, width=80, height=25)
text_output.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()
