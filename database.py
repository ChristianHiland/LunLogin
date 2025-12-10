from sqlite3 import Connection, Cursor
from pydantic import BaseModel
from io import BytesIO
from typing import Any
from enum import Enum
import sqlite3
import zipfile
import json
import os

class AssetTypes(str, Enum):
    PFP = "pfp"
    STICKER = "sticker"
    ASSET_BUNDLE = "asset_bundle"
    WORLD = "world"

class WorldInfo(BaseModel):
    name: str | None = None
    publisher: str | None = None
    bundlepath: str | None = None
    bundledata: str | None = None

    def from_string(self, string: str):
        data = json.loads(string)
        try:
            return WorldInfo(**data)
        except Exception as e:
            print(f"[ERROR]: {e}")

    def to_json(self):
        return {"name": self.name, "publisher": self.publisher, "bundlepath": self.bundlepath, "bundledata": self.bundledata}

    def package_data(self, worldInfo):
        with open(worldInfo, "r") as dataFile:
            data = json.load(dataFile)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as ZipFile:
                ZipFile.write(data["bundlepath"])
                ZipFile.write(data["bundledata"])
                ZipFile.write(worldInfo)
            zip_buffer.seek(0)
            return zip_buffer

class User(BaseModel):
    name: str
    username: str
    password: str
    email: str | None = None
    userdata: str | None = None

class UserDatabase:
    def __init__(self, db_file: str):
        self.db_file: str = db_file
        self.connection: Connection = None
        self.cursor: Cursor = None
        self.baseUserData = "Data/Users/"

    def Connect(self):
        if self.connection == None and self.cursor == None:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()

    def Disconnect(self):
        self.connection.close()

    def AddUser(self, name: str, username: str, password: str, email: str, options: dict = {}, rank: str = "Vistor"):
        userdata_path = os.path.join(self.baseUserData, username + ".json")
        with open(userdata_path, "w") as file:
            temp_data = {"DisplayName": name, "Assets": {"pfp": "Data/Media/ProfileIcons/Default.png"}, "Options": options}
            temp_data["Options"]["Rank"] = rank
            json.dump(temp_data, file, indent=4)
        try:
            self.cursor.execute("INSERT INTO users (name, username, password, email, userdata) VALUES (?, ?, ?, ?, ?)", (name, username, password, email, userdata_path))
            self.connection.commit()
            print(f"User {username} has been registered.")
        except sqlite3.IntegrityError:
            print(f"[SQ LITE ERROR]: Username already exists.")

    def GetUser(self, username: str = None) -> tuple[User, Any]:
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        userObj = User(name=user[1], username=user[2], password=user[3], email=user[4], userdata=user[5])
        with open(userObj.userdata, "r") as file:
            return (userObj, json.load(file))
    
    def DeleteUser(self, username: str):
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        userdata_path = os.path.join(self.baseUserData, username + ".json")
        userdata_profile = os.path.join("Data/Media/ProfileIcons", username + ".png")
        os.remove(userdata_path)
        os.remove(userdata_profile)
        self.connection.commit()

    def PackageAssets(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        userObj = User(name=user[1], username=user[2], password=user[3], email=user[4], userdata=user[5])
        with open(userObj.userdata, "r") as file:
            data = json.load(file)
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w") as assetZip:
                assetZip.write(data["Assets"]["pfp"], os.path.relpath(data["Assets"]["pfp"], "Data/"))
                assetZip.write(userObj.userdata, os.path.relpath(userObj.userdata, "Data/"))
            zip_buffer.seek(0)
            return zip_buffer