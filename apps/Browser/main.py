import customtkinter as ctk
from tkinterweb import HtmlFrame  # pure tkinter widget, works inside CTkFrame
import tkinter as tk

APP_WIDTH = 800
APP_HEIGHT = 600

def launch_app(parent):
    # Create address bar container
    top_bar = ctk.CTkFrame(parent)
    top_bar.pack(fill="x", padx=5, pady=5)

    url_var = ctk.StringVar(value="https://www.google.com")

    # Address bar entry
    url_entry = ctk.CTkEntry(top_bar, textvariable=url_var)
    url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

    # Go button
    def load_url():
        url = url_var.get()
        if not (url.startswith("http://") or url.startswith("https://")):
            url = "http://" + url
        browser.load_website(url)

    go_btn = ctk.CTkButton(top_bar, text="Go", width=50, command=load_url)
    go_btn.pack(side="right")

    # Browser frame (tkinterweb HtmlFrame)
    browser = HtmlFrame(parent, horizontal_scrollbar="auto")
    browser.pack(fill="both", expand=True, padx=5, pady=5)

    # Load default page
    browser.load_website(url_var.get())

    # Enter key triggers load
    url_entry.bind("<Return>", lambda e: load_url())
