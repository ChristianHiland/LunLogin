from pydantic import BaseModel
from pathlib import Path
from io import BytesIO
import zipfile
import json
import os

class AvatarStruct(BaseModel):
    name: str | None = None
    publisher: str | None = None
    avatarpath: str | None = None
    platform: str | None = "StandaloneWindows64"
    avatarthumbnail: str | None = "Data/Media/AvatarIcons/Default.png"

    def to_json(self):
        return {"name": self.name, "publisher": self.publisher, "avatarpath": self.avatarpath, "avatarthumbnail": self.avatarthumbnail}
    
    def read(self, path):
        with open(path, "r") as file:
            return json.load(file)

    def write(self, path: str, data):
        with open(path, "w") as file:
            json.dump(data, file, indent=4)

    def update_thumbnail(self, data_path: str, thumbnail_path: str):
        data = self.read(data_path)
        data["avatarthumbnail"] = thumbnail_path
        self.write(data_path, data)

    def package_data(self, avatarInfo: str):
        with open(avatarInfo, "r") as avatarData:
            data = json.load(avatarData)
            zip_buffer = BytesIO()
            avatarBundle = Path(data["avatarpath"])
            avatarInfo = Path(avatarInfo)
            with zipfile.ZipFile(zip_buffer, "w") as ZipFile:
                ZipFile.write(avatarBundle, "avatar.socialAvatar")
                ZipFile.write(avatarInfo, avatarInfo.name)
            
            zip_buffer.seek(0, 2)
            file_size = zip_buffer.tell()
            zip_buffer.seek(0)
            return zip_buffer, file_size
    
    def get_thumbnail(self, avatarInfo: str):
        buffer = BytesIO()
        with open(avatarInfo, "r") as avatarFile:
            data = json.load(avatarFile)
            with open(Path(data["avatarthumbnail"]), "rb") as file:
                buffer = BytesIO(file.read())
                file_size = os.path.getsize(Path(data["avatarthumbnail"]))
                return buffer, file_size
