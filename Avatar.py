from pathlib import Path
from pydantic import BaseModel
from io import BytesIO
import zipfile
import json

class Avatar(BaseModel):
    name: str | None = None
    publisher: str | None = None
    avatarpath: str | None = None
    avatarthumbnail: str | None = "Data/Media/AvatarIcons/Default.png"

    def save_data(self):
        with open(Path("Data/Game/Avatars/", f"{self.publisher}/{self.name}/avatar.json"), "w")