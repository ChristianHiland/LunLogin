import json

class OnlineMangment:
    def __init__(self, currentOnlineInstFile: str):
        self.currentOnlineInst = {"OnlineInstances": []}
        with open(currentOnlineInstFile, "r") as file:
            self.currentOnlineInst = json.load(file)

    def AddInstance(self, worldName: str, publisher: str, instanceName: str, instance_code: str):
        temp = {"World": {"worldName": worldName, "publisher": publisher}, "Lobbies": [{"Instance": instanceName, "Author": "[BETA TESTING]", "joinCode": instance_code}]}
        if temp not in self.currentOnlineInst["OnlineInstances"]:
            self.currentOnlineInst["OnlineInstances"].append(temp)

    def RemoveInstance(self, worldName: str, publisher: str, instanceName: str, instance_code: str):
        temp = {"World": {"worldName": worldName, "publisher": publisher}, "Lobbies": [{"Instance": instanceName, "Author": "[BETA TESTING]", "joinCode": instance_code}]}
        if temp in self.currentOnlineInst["OnlineInstances"]:
            self.currentOnlineInst["OnlineInstances"].remove(temp)

    def GetInstances(self, worldName: str, publisher: str):
        instances = []
        for instance in self.currentOnlineInst["OnlineInstances"]:
            if instance["worldName"] == worldName and instance["publisher"] == publisher:
                instances.append(instance)
        return instances