from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from database import UserDatabase, User, WorldInfo, LoginFormat
from fastapi.responses import StreamingResponse
from Online import OnlineMangment
from Avatar import AvatarStruct
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
    return "online"

#
# World Mangment
#

@app.post('/game/assets/uploadWorld')
async def UploadWorldAsset(worldInfo_str: str = Form(...), platform: str = Form(...), file: UploadFile = File(...)):
    """Upload World Asset, along with world info as string. {"name": val, "publisher": val}"""
    worldInfo = WorldInfo().from_string(worldInfo_str)
    if worldInfo.worldthumbnail == None:
        worldInfo.worldthumbnail = "Data/Game/Worlds/DefaultWorld.png"
    savePath = Path("Data/Game/Worlds/") / worldInfo.publisher / worldInfo.name
    print(f"Saving at: {savePath}")
    savePath.mkdir(parents=True, exist_ok=True)
    try:
        with open(savePath / platform / file.filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        with open(savePath / "world.info", "w") as infoFile:
            worldInfo.bundlepath = savePath.__str__() + f"/{file.filename}"
            worldInfo.bundledata = savePath.__str__() + f"/{file.filename.replace(".socialworld", ".socialdata")}"
            json.dump(worldInfo.to_json(), infoFile, indent=4)
        worldInfo.updateGlobalInfo()
    finally:
        await file.close()

@app.get('/game/assets/getWorld')
async def GetWorldAsset(worldName: str = Form(...), publisher: str = Form(...), platform: str = Form(...)):
    """Get World Asset in zip file format, using world Name, Publisher, and Platform."""
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
