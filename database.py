from sqlite3 import Connection, Cursor
from pydantic import BaseModel
from pathlib import Path
from io import BytesIO
from typing import Any
import sqlite3
import zipfile
import json
import os

class WorldInfo(BaseModel):
    name: str | None = None
    publisher: str | None = None
    scene: str | None = None
    bundlepath: str | None = None
    bundledata: str | None = None
    worldthumbnail: str | None = None

    def from_string(self, string: str):
        data = json.loads(string)
        try:
            return WorldInfo(**data)
        except Exception as e:
            print(f"[ERROR]: {e}")
            
    def updateGlobalInfo(self):
        oldData = self.read("globalWorld.info")
        temp = {"name": self.name, "publisher": self.publisher}
        if temp not in oldData["Worlds"]:
            oldData["Worlds"].append(temp)
            
            with open("globalWorld.info", "w") as file:
                json.dump(oldData, file, indent=4)

    def updateThumbnail(self, worldInfo, thumbnailPath: Path):
        oldData = self.read(worldInfo)
        oldData["worldthumbnail"] = thumbnailPath.__str__()
        with open(worldInfo, "w") as file:
            json.dump(oldData, file, indent=4)
        
    def read(self, file: str):
        with open(file, "r") as file:
            return json.load(file)

    def to_json(self):
        return {"name": self.name, "publisher": self.publisher, "scene": self.scene, "bundlepath": self.bundlepath, "bundledata": self.bundledata, "worldthumbnail": self.worldthumbnail}

    def package_data(self, worldInfo):
        """Package World into Zip: Containing: Bundle Assets, Thumbnail, World Info Json"""
        with open(worldInfo, "r") as dataFile:
            data = json.load(dataFile)
            zip_buffer = BytesIO()
            bundlescene = Path(data["bundlepath"])
            worldinfo = Path(worldInfo)
            with zipfile.ZipFile(zip_buffer, "w") as ZipFile:
                ZipFile.write(bundlescene, "world.socialWorld")
                #ZipFile.write(data["bundledata"])
                #ZipFile.write(data["worldthumbnail"])
                ZipFile.write(worldinfo, worldinfo.name)
            zip_buffer.seek(0, 2)
            file_size = zip_buffer.tell()
            zip_buffer.seek(0)
            return zip_buffer, file_size
    
    def get_thumbnail(self, worldInfo):
        buffer = BytesIO()
        with open(worldInfo, "r") as infoFile:
            data = json.load(infoFile)
            thumbnailPath = Path(data["worldthumbnail"])
            with open(thumbnailPath, "rb") as file:
                buffer = BytesIO(file.read())
                file_size = os.path.getsize(thumbnailPath)
                return buffer, file_size

class User(BaseModel):
    name: str | None = None
    username: str | None = None
    password: str | None = None
    email: str | None = None
    userdata: str | None = None
    defaultWorld: str | None = None
    avatar: str | None = "defaultAvatar"
    rank: str | None = "guest"
    
    def from_string(self, string):
        data = json.loads(string)
        try:
            return User(**data)
        except Exception as e:
            print(f"[ERROR]: {e}")
            
class LoginFormat(BaseModel):
    username: str
    password: str


class UserDatabase:
    def __init__(self, db_file: str):
        self.db_file: str = db_file
        self.connection: Connection = None
        self.cursor: Cursor = None
        self.baseUserData = "Data/Users/"

    # sqlite Functions
    def Connect(self):
        if self.connection == None and self.cursor == None:
            self.connection = sqlite3.connect(self.db_file)
            self.cursor = self.connection.cursor()

    def Disconnect(self):
        self.connection.close()

    def AddUser(self, name: str, username: str, password: str, email: str, options: dict = {}, rank: str = "Vistor"):
        userdata_path = os.path.join(self.baseUserData, username + ".json")
        with open(userdata_path, "w") as file:
            temp_data = {"DisplayName": name, "Assets": {"pfp": "Data/Media/ProfileIcons/Default.png", "Stickers": []}, "Options": options}
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
        userdata_stickers = os.path.join(f"Data/Users/{username}/Stickers")
        os.remove(userdata_path)
        os.remove(userdata_profile)
        os.remove(userdata_stickers)
        self.connection.commit()

    # Asset and Data Management
    def GetUserJSON(self, username: str):
        """Get user data from the json."""
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        with open(user[5], "r") as file:
            return json.load(file)
        
    def SaveUserJSON(self, data, username: str):
        self.cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = self.cursor.fetchone()
        with open(user[5], "w") as file:
            json.dump(data, file, indent=4)

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