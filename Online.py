import json

class OnlineMangment:
    def __init__(self, currentOnlineInstFile: str):
        self.currentOnlineInstFile = currentOnlineInstFile
        self.currentOnlineInst = {"OnlineInstances": []}
        try:
            with open(currentOnlineInstFile, "r") as file:
                self.currentOnlineInst = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # If file doesn't exist or is empty, start with a clean structure
            self.Save()

    def AddInstance(self, worldName: str, publisher: str, owner: str, instanceName: str, instanceId: int):
        tempRoom = {"InstanceName": instanceName, "Owner": owner, "InstanceID": instanceId}
        
        target_instance = None
        # Find if the world already exists in our list
        for instance in self.currentOnlineInst["OnlineInstances"]:
            world_data = instance.get("World", {})
            if world_data.get("worldName") == worldName and world_data.get("publisher") == publisher:
                target_instance = instance
                break
        
        if target_instance:
            # Check if Room ID already exists to prevent duplicates (Optional but recommended)
            if not any(r.get("InstanceID") == instanceId for r in target_instance["Rooms"]):
                target_instance["Rooms"].append(tempRoom)
        else:
            # Create a brand new world entry
            new_entry = {
                "World": {"worldName": worldName, "publisher": publisher}, 
                "Rooms": [tempRoom]
            }
            self.currentOnlineInst["OnlineInstances"].append(new_entry)

        self.Save()

    def RemoveRoom(self, target_world: str, target_pub: str, target_id: int):
        for entry in self.currentOnlineInst.get("OnlineInstances", []):
            world = entry.get("World", {})
            
            if world.get("worldName") == target_world and world.get("publisher") == target_pub:
                original_count = len(entry["Rooms"])
                # Filter out the room
                entry["Rooms"] = [room for room in entry["Rooms"] if room.get("InstanceID") != target_id]
                
                if len(entry["Rooms"]) < original_count:
                    print(f"Success: Room {target_id} removed.")
                    self.Save() # Make sure to save after removal!
                    return True
                    
        print(f"Error: No matching World '{target_world}' or InstanceID {target_id} found.")
        return False

    def GetInstances(self, worldName: str, publisher: str):
        # This returns the list of Rooms for a specific world
        for instance in self.currentOnlineInst["OnlineInstances"]:
            world_data = instance.get("World", {})
            if world_data.get("worldName") == worldName and world_data.get("publisher") == publisher:
                return instance.get("Rooms", [])
        return []

    def CheckInstance(self, worldName: str, publisher: str, instanceID: str):
        doesExist = False
        for instance in self.currentOnlineInst["OnlineInstances"]:
            world_data = instance.get("World", {})
            if world_data.get("worldName") == worldName and world_data.get("publisher") == publisher and world_data.get("InstanceID") == instanceID:
                doesExist = True

        return doesExist
        
    def Save(self):
        with open(self.currentOnlineInstFile, "w") as file:
            json.dump(self.currentOnlineInst, file, indent=4)

    def world_exists(self, target_name: str, target_publisher: str) -> bool:
        return any(
            entry.get("World", {}).get("worldName") == target_name and 
            entry.get("World", {}).get("publisher") == target_publisher 
            for entry in self.currentOnlineInst.get("OnlineInstances", [])
        )
