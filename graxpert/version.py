import requests
from graxpert.localization import _
from tkinter import messagebox
from datetime import datetime

release = "RELEASE"
version = "SNAPSHOT"


def check_for_new_version():
    try:
        response = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/latest")
        latest_release_date = datetime.strptime(response.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        
        response_current = requests.get("https://api.github.com/repos/Steffenhir/GraXpert/releases/tags/" + version)
        current_release_date = datetime.strptime(response_current.json()["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        current_is_beta = response_current.json()["prerelease"]
        
        if current_is_beta:
            if current_release_date >= latest_release_date:
                messagebox.showinfo(title = _("This is a Beta release!"),
                                    message= _("Please note that this is a Beta release of GraXpert. You will be notified when a newer official version is available."))
            else:
                messagebox.showinfo(title = _("New official release available!"),
                                    message= _("This Beta version is deprecated. A newer official release of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest")
                                               
                                    
        
        elif latest_release_date > current_release_date:
            messagebox.showinfo(title = _("New version available!"),
                                message= _("A newer version of GraXpert is available at") + " https://github.com/Steffenhir/GraXpert/releases/latest")
    except:
        print("Could not check for newest version")