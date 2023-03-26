import requests
from localization import _
from tkinter import messagebox

release = "RELEASE"
version = "SNAPSHOT"


def check_for_new_version():
    try:
        response = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/latest")
        newest_version = response.json()["name"]
        
        if newest_version != version:
            messagebox.showinfo(title = "New version available!",
                                message= _("A newer version of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest")
    except:
        print("Could not check for newest version")