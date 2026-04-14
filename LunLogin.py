from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from database import UserDatabase, User, WorldInfo, LoginFormat
from fastapi.responses import StreamingResponse
from Online import OnlineMangment
from pathlib import Path
import shutil
import json
import os

# FastAPI
print("Starting FastAPI")
app = FastAPI()
# Database
print("Starting sqlite3 database")
userDB = UserDatabase("Data/users.db")
userDB.Connect()
# Online Managment
print("Starting Online Managment")
onlineManager = OnlineMangment("currentOnlineInst.info")


@app.get('/')
async def root():
    return {"status": "online"}

#
# Login Mangment
#

@app.post('/user/login/')
async def UserLogin(username: str = Form(...), password: str = Form(...)):
    user = userDB.GetUser(username)
    if user[0].password == password:
        return user[1]

@app.post('/user/signup/')
async def UserSignup(name: str = Form(...), username: str = Form(...), password: str = Form(...)):
    """Create a new user and add it to the database"""
    user = User(name = name, username = username, password = password)
    userDB.AddUser(user.name, user.username, user.password, user.email)
    user = userDB.GetUser(username)
    return user[0]

@app.post('/user/delete/')
async def UserRemove(username: str):
    userDB.DeleteUser(username)

#
# User Asset Managment
#

@app.get('/user/assets/get')
async def GetUserAssets(username: str):
    """Get User Data, and package it into a zip"""
    zip = userDB.PackageAssets(username)
    headers = {'Content-Disposition': 'attachment; filename="userAssets.zip"'}
    return StreamingResponse(zip, media_type="application/zip", headers=headers)

@app.post('/user/assets/upload/pfp')
async def UploadUserPFP(username: str, file: UploadFile = File(...)):
    """Upload a User Profile Icon to The Server."""
    savePath = Path(f"Data/Media/ProfileIcons/{username}.png")
    try:
        with open(savePath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        user_json = userDB.GetUserJSON(username)
        user_json["Assets"]["pfp"] = savePath.__str__()
        userDB.SaveUserJSON(user_json, username)
    finally:
        await file.close()

@app.post('/users/assets/upload/sticker')
async def UploadUserSticker(username: str, file: UploadFile = File(...)):
    """Upload a user sticker"""
    savePath = Path(f"Data/Users/{username}/Stickers/")
    savePath.mkdir(parents=True, exist_ok=True)
    with open(savePath / file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Update User's Stickers.
    user_json = userDB.GetUserJSON(username)
    stickers: list[str] = user_json["Assets"]["Stickers"]
    stickers.append(savePath.__str__() + file.filename)
    user_json["Assets"]["Stickers"] = stickers
    userDB.SaveUserJSON(user_json, username)
    await file.close()

#
# Game Asset Managment
#

@app.post('/game/assets/uploadWorld')
async def UploadWorldAsset(worldInfo_str: str = Form(...), file: UploadFile = File(...)):
    """Upload World Asset, along with world info as string. {"name": val, "publisher": val}"""
    worldInfo = WorldInfo().from_string(worldInfo_str)
    if worldInfo.worldthumbnail == None:
        worldInfo.worldthumbnail = "Data/Game/Worlds/DefaultWorld.png"
    savePath = Path("Data/Game/Worlds/") / worldInfo.publisher / worldInfo.name
    savePath.mkdir(parents=True, exist_ok=True)
    try:
        with open(savePath / file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with open(savePath / "world.info", "w") as infoFile:
            worldInfo.bundlepath = savePath.__str__() + f"/{file.filename}"
            worldInfo.bundledata = savePath.__str__() + f"/{file.filename.replace(".socialworld", ".socialdata")}"
            json.dump(worldInfo.to_json(), infoFile, indent=4)
        worldInfo.updateGlobalInfo()
    finally:
        await file.close()

@app.get('/game/assets/getWorld')
async def GetWorldAsset(worldName: str, publisher: str):
    """Get World Asset in zip file format, using world Name, and Publisher."""
    print(f"name: {worldName}, publisher: {publisher}")
    worldFolder = Path(f"Data/Game/Worlds/{worldName}/{publisher}/world.info")
    zip, file_size = WorldInfo().package_data(worldFolder)
    headers = {'Content-Disposition': f'attachment; filename="{worldName}.zip"', 'Content-Length': str(file_size)}
    return StreamingResponse(zip, media_type="application/zip", headers=headers)

@app.get('/game/assets/getWorldThumbnail')
async def GetWorldThumbnail(worldName: str, publisher: str):
    """Get a world's thumbnail and upload it."""
    worldInfo = Path(f"Data/Game/Worlds/{publisher}/{worldName}/world.info")
    img, file_size = WorldInfo().get_thumbnail(worldInfo)
    headers = {'Content-Disposition': f'attachment; filename="{worldName}_{publisher}.png"', 'Content-Length': str(file_size)}
    return StreamingResponse(img, media_type="application/image", headers=headers)

@app.post('/game/assets/uploadWorldThumbnail')
async def UploadWorldThumbnail(worldName: str = Form(...), publisher: str = Form(...), file: UploadFile = File(...)):
    """Get a world's thumbnail and upload it."""
    worldInfo = Path(f"Data/Game/Worlds/{publisher}/{worldName}/world.info")
    worldPath = Path(f"Data/Game/Worlds/{publisher}/{worldName}/")
    with open(worldPath / f"image.png", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    WorldInfo().updateThumbnail(worldInfo, worldPath / "image.png")

@app.get('/game/assets/getWorldList')
async def GetWorldList():
    """Get a list of world along with their publishers."""
    with open("globalWorld.info", "r") as file:
        return json.load(file)
            
@app.post('/game/assets/getWorldSize')
async def GetWorldSize(worldName: str = Form(...), publisher: str = Form(...)):
    worldFile = Path(f"Data/Game/Worlds/{publisher}/{worldName}/{worldName}")
    return os.path.getsize(worldFile)

#
# Online Managment
#

@app.post('/game/online/createInstance')
async def CreateInstance(worldName: str = Form(...), publisher: str = Form(...), owner: str = Form(...), instanceName: str = Form(...), instanceID: str = Form(...)):
    onlineManager.AddInstance(worldName, publisher, owner, instanceName, instanceID)

@app.post('/game/online/removeInstance')
async def RemoveInstance(worldName: str = Form(...), publisher: str = Form(...), instanceID: str = Form(...)):
    onlineManager.RemoveRoom(worldName, publisher, instanceID)

@app.post('/game/online/getInstances')
async def GetInstances(worldName: str = Form(...), publisher: str = Form(...)):
    # Returns [{"InstanceName": instanceName, "Owner": owner, "InstanceID": instanceId}]
    tempRooms = {"Rooms": onlineManager.GetInstances(worldName, publisher)}
    return tempRooms

