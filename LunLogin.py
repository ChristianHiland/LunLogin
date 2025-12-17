from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from database import UserDatabase, User, WorldInfo, LoginFormat
from fastapi.responses import StreamingResponse
from pathlib import Path
import shutil
import json
import os

app = FastAPI()
userDB = UserDatabase("Data/users.db")
userDB.Connect()


@app.get('/')
async def root():
    return {"status": "online"}

@app.post('/user/test/')
async def UserLogin(request: Request): 
    # Read the raw body as text
    raw_body = await request.body()

    # Decode the bytes to a string
    body_string = raw_body.decode('utf-8')

    print("--- SERVER RECEIVED RAW BODY ---")
    print(f"Content-Type: {request.headers.get('content-type')}")
    print(f"Raw String: {body_string}")
    print("--------------------------------")

    # If the request makes it here, you should see the JSON string printed.
    return {"message": "Raw body received successfully."}

#
# Login Mangment
#

@app.post('/user/login/')
async def UserLogin(data: LoginFormat):
    print(data)
    user = userDB.GetUser(data.username)
    if user[0].password == data.password:
        return user[0]

@app.post('/user/signup/')
async def UserSignup(userInfo: str = Form(...)):
    """Create a new user and add it to the database"""
    user = User().from_string(userInfo)
    userDB.AddUser(user.name, user.username, user.password, user.email)

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
    savePath = Path("Data/Game/Worlds/") / worldInfo.publisher / worldInfo.name
    savePath.mkdir(parents=True, exist_ok=True)
    try:
        with open(savePath / file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with open(savePath / "world.info", "w") as infoFile:
            worldInfo.bundlepath = savePath.__str__() + f"\\{file.filename}"
            worldInfo.bundledata = savePath.__str__() + f"\\{file.filename.replace(".socialworld", ".socialdata")}"
            json.dump(worldInfo.to_json(), infoFile, indent=4)
        worldInfo.updateGlobalInfo()
    finally:
        await file.close()

@app.get('/game/assets/getWorld')
async def GetWorldAsset(worldName: str, publisher: str):
    """Get World Asset in zip file format, using world Name, and Publisher."""
    print(f"name: {worldName}, publisher: {publisher}")
    worldFolder = Path(f"Data/Game/Worlds/{worldName}/{publisher}/world.info")
    zip = WorldInfo().package_data(worldFolder)
    headers = {'Content-Disposition': f'attachment; filename="{worldName}.zip"'}
    return StreamingResponse(zip, media_type="application/zip", headers=headers)

@app.get('/game/assets/getWorldList')
async def GetWorldList():
    """Get a list of world along with their publishers."""
    with open("globalWorld.info", "r") as file:
        return json.load(file)
    
    #content = {"worlds": []}
    #for item in Path("Data/Game/Worlds").iterdir():
    #    if item.is_dir():
    #        publisher_folder_name = item.name
    #        contents = []
    #        for world in item.iterdir():
    #            if world.is_dir():
    #                contents.append(world.name)
    #        content["worlds"].append({"publisher": publisher_folder_name, "world_names": contents})

    return content
            