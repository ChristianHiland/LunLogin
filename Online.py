import json

class OnlineMangment:
    def __init__(self, currentOnlineInstFile: str):
        self.currentOnlineInstFile = currentOnlineInstFile
        self.currentOnlineInst = {"OnlineInstances": []}
        with open(currentOnlineInstFile, "r") as file:
            self.currentOnlineInst = json.load(file)

    def AddInstance(self, worldName: str, publisher: str, instanceName: str, instance_code: str):
        temp = {"World": {"worldName": worldName, "publisher": publisher}, "Lobbies": [{"Instance": instanceName, "Author": "[BETA TESTING]", "joinCode": instance_code}]}
        if temp not in self.currentOnlineInst["OnlineInstances"]:
            self.currentOnlineInst["OnlineInstances"].append(temp)
            self.Save()

    def RemoveInstance(self, worldName: str, publisher: str, instanceName: str, instance_code: str):
        temp = {"World": {"worldName": worldName, "publisher": publisher}, "Lobbies": [{"Instance": instanceName, "Author": "[BETA TESTING]", "joinCode": instance_code}]}
        if temp in self.currentOnlineInst["OnlineInstances"]:
            self.currentOnlineInst["OnlineInstances"].remove(temp)
            self.Save()

    def GetInstances(self, worldName: str, publisher: str):
        instances = []
        for instance in self.currentOnlineInst["OnlineInstances"]:
            if instance["worldName"] == worldName and instance["publisher"] == publisher:
                instances.append(instance)
        return instances
    
    def Save(self):
        with open(self.currentOnlineInstFile, "w") as file:
            json.dump(self.currentOnlineInst, file, indent=4)