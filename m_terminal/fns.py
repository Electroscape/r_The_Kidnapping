import os
import requests
from flask import json


def js_r(filename: str, auth="", from_static=True, add_buttons=True) -> dict:
    """
    json read function is used to get the json data from a file and load it to a dict

    :param add_buttons: only for html templates
    :param from_static: (bool) from static folder or not
    :param auth: authenticated user
    :param filename: json file name inside static folder
    :return: dict or None
    """

    if from_static:
        filename = f"static/{filename}"

    try:
        with open(filename, "r") as f_in:
            json_data = json.load(f_in)
            if add_buttons:
                json_data["btns"] = configure_btns(json_data.get("btns"), auth)
        return json_data

    except IOError:
        return {}


def configure_btns(data: list, auth=""):
    with open("templates/ControlPanel.html", "r") as f_in:
        options_html = f_in.read()

    for d in data:
        # get default html
        txt = options_html
        # create ids
        d.update({"id": d.get("link").replace("_", "-")})
        # change authenticated user
        if d["auth"] and auth == d["auth"].lower():
            d["auth"] = False

        keys = {
            "control.id": d.get("id"),
            "control.image": d.get("image"),
            "control.details": d.get("details"),
            "control.title": d.get("title"),
            "control.link": d.get("link")
        }
        for k, v in keys.items():
            txt = txt.replace(k, v)
        d.update({"html": txt})

    return data


def configure_btn(d: dict):
    with open("templates/ControlPanel.html", "r") as f_in:
        html = f_in.read()

    # create ids
    d.update({"id": d.get("link").replace("_", "-")})

    keys = {
        "control.id": d.get("id"),
        "control.image": d.get("image"),
        "control.details": d.get("details"),
        "control.title": d.get("title"),
        "control.link": d.get("link")
    }
    for k, v in keys.items():
        html = html.replace(k, v)
    d.update({"html": html})

    return d


def listdir_no_hidden(path):
    return [f for f in os.listdir(path) if not f.startswith('.')]

versions = js_r("json/ver_config.json", add_buttons=False)



def get_progressbar_status():
    percentage = requests.get(f"{server_ip}/get_progress").json()
    return percentage.get("percent", 100)


def is_unique_users() -> bool:
    login_users = requests.get(f"{server_ip}/get_auth_users").json()
    users = login_users.values()

    if "empty" not in users and len(set(users)) == 2:
        return True
    else:
        return False


def get_login_users() -> dict:
    try:
        users = requests.get(f"{server_ip}/get_auth_users").json()
    except Exception as e:
        users = {}
    return users


def get_version(ter_name) -> dict:
    return versions.get(ter_name, {})
