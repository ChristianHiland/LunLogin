from database import UserDatabase, User, AssetTypes, WorldInfo
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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

#
# Login Mangment
#

@app.get('/user/login/')
async def UserLogin(username: str, password: str):
    user = userDB.GetUser(username)
    if user[0].password == password:
        return user

@app.post('/user/signup/')
async def UserSignup(userInfo: User):
    """Create a new user and add it to the database"""
    userDB.AddUser(userInfo.name, userInfo.username, userInfo.password, userInfo.email)

@app.post('/user/delete/')
async def UserRemove(username: str):
    userDB.DeleteUser(username)


#
# Asset Managment
#

@app.get('/user/assets/get')
async def GetUserAssets(username: str):
    zip = userDB.PackageAssets(username)
    headers = {'Content-Disposition': 'attachment; filename="userAssets.zip"'}
    return StreamingResponse(zip, media_type="application/zip", headers=headers)

@app.post('/user/assets/upload')
async def UploadUserAsset(username: str, assetType: AssetTypes, file: UploadFile = File(...)):
    # Finding out the path based on the Asset Type
    savePath = Path("")
    if assetType is AssetTypes.PFP:
        savePath = Path(f"Data/Media/ProfileIcons/{username}.png")
    elif assetType is AssetTypes.STICKER:
        savePath = Path(f"Data/Media/Stickers/{username}/")
        savePath.mkdir(parents=True, exist_ok=True)
        savePath = savePath / file.filename
    else:
        savePath = Path(f"Data/Errored/{file.filename}")

    # Saving File
    try:
        with open(savePath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
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
    finally:
        await file.close()

@app.get('/game/assets/getWorld')
async def GetWorldAsset(worldName: str, publisher: str):
    """Get World Asset in zip file format, using world Name, and Publisher."""
    worldFolder = Path(f"Data/Game/Worlds/{publisher}/{worldName}/world.info")
    zip = WorldInfo().package_data(worldFolder)
    headers = {'Content-Disposition': f'attachment; filename="{worldName}.zip"'}
    return StreamingResponse(zip, media_type="application/zip", headers=headers)

