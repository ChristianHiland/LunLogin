using UnityEngine.Networking;
using System.IO.Compression;
using System.Collections;
using UnityEngine;
using System.IO;

namespace SocialSDK {

    [System.Serializable]
    public class UserData {
        public string name;
        public string username;
        public string password;
        public string email;
        public string userdata;
    }

    [System.Serializable]
    public class WorldData {
        public string name;
        public string publisher;
        public string bundlepath;
        public string bundledata;
        public string worldthumbnail;
    }

    public class UserLogin {
        public string username;
        public string password;
    }
    
    public class GetWorld {
        public string publisher;
        public List<string> world_names;
    }

    public class GetWorldData {
        public List<GetWorld> worlds;
    }

    public class API : MonoBehaviour {
        
        private const string ServerURL = "http://127.0.0.1:8001/";

        // Locations for File Data
        public string WorldPath = Application.persistentDataPath + "Worlds/";
        public string UserPath = Application.persistentDataPath + "User/";

        public string UserLoginData;
        public string WorldListData;

        // Downloading a World and Unzipping it into the WorldPath with the extract folder named: worldName_publisher/

        public void DownloadWorld(string worldName, string publisher) {
            StartCoroutine(DownloadWorldCo(worldName, publisher));
        }

        private IEnumerator DownloadWorldCo(string worldName, string publisher) {
            using (var uwr = new UnityWebRequest(ServerURL + "game/assets/getWorld", UnityWebRequest.kHttpVerbGET)) {
                uwr.downloadHandler = new DownloadHandlerFile(WorldPath + $"{worldName}_{publisher}.zip");
                yield return uwr.SendWebRequest();
                if (uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocoalError) { Debug.LogError($"Download Error: {uwr.error}"); }
                if (!Directory.Exists(WorldPath + $"{worldName}_{publisher}")) { Directory.CreateDirectory(WorldPath + $"{worldName}_{publisher}"); }
                ZipFile.ExtractToDirectory(WorldPath + $"{worldName}_{publisher}.zip", WorldPath + $"{worldName}_{publisher}", overwriteFiles: true);
            }
        }

        // Getting a list of worlds
        public GetWorldData GetWorldsOnServer() {
            StartCoroutine(GetWorldsOnServerCo());
            return JsonUtility.FromJson<GetWorldData>(WorldListData);
        }

        private IEnumerator GetWorldsOnServerCo() {
            using (var uwr = new UnityWebRequest(ServerURL + "game/assets/getWorldList", UnityWebRequest.kHttpVerbGET)) {
                uwr.SetRequestHeader("Content-Type", "application/json");
                uwr.downloadHandler = new DownloadHandlerBuffer();
                yield return uwr.SendWebRequest();
                if (uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocoalError) { Debug.LogError($"Download Error: {uwr.error}"); }
                WorldListData = uwr.downloadHandler.text;
            }
        }

        // Downloading User Data, and unziping it into the UserPath, with extract folder named: username/

        public void DownloadUser(string username) {
            StartCoroutine(DownloadUserCo(username));
        }

        private IEnumerator DownloadUserCo(string username) {
            using (var uwr = new UnityWebRequest(ServerURL + "user/assets/get", UnityWebRequest.kHttpVerbGET)) {
                uwr.downloadHandler = new DownloadHandlerFile(UserPath + $"{username}.zip");
                yield return uwr.SendWebRequest();
                if (uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocoalError) { Debug.LogError($"Download Error: {uwr.error}"); }
                if (!Directory.Exists(UserPath + $"{username}")) { Directory.CreateDirectory(UserPath + $"{username}"); }
                ZipFile.ExtractToDirectory(UserPath + $"{username}.zip", UserPath + $"{username}", overwriteFiles: true);
            }
        }

        // Login in function

        public UserData Login(string username, string password) {
            StartCoroutine(LoginCo(username, password));
            return JsonUtility.FromJson<UserLogin>(UserLoginData);
        }

        private IEnumerator LoginCo(string username, string password) {
            UserLogin loginPayload = new UserLogin { username = username, password = password};
            string jsonPayload = JsonUtility.ToJson(loginPayload);
            byte[] rawBody = Encoding.UTF8.GetBytes(jsonPayload);
            using (var uwr = new UnityWebRequest(ServerURL + "user/login", UnityWebRequest.kHttpVerbGET)) {
                uwr.uploadHandler = new UploadHandlerRaw(rawBody);
                uwr.SetRequestHeader("Content-Type", "application/json");
                uwr.downloadHandler = new DownloadHandlerBuffer();
                yield return uwr.SendWebRequest();
                if (uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocoalError) { Debug.LogError($"Download Error: {uwr.error}"); }
                UserLoginData = uwr.downloadHandler.text;
            }
        }
    }
}