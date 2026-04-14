using System.Collections.Generic;
using Photon.Realtime;
using UnityEngine;
using Photon.Pun;

namespace SocialSDK {
    public class Multiplayer : MonoBehaviourPunCallbacks {
        public string ownerDisplayName = "";

        public SocialVRPlayer socialVRPlayer;
        public WorldHandler worldHandler;

        public void CreateInstance(string worldName, string publisher) {
            int instanceID = 0;
            string roomName = $"{publisher}_{worldName}_{instanceID}";

            RoomOptions options = new RoomOptions();
            options.MaxPlayers = 20;

            // Storing world Metadata.
            ExitGames.Client.Photon.Hashtable roomProps = new ExitGames.Client.Photon.Hashtable();
            roomProps.Add("w_name", worldName);
            roomProps.Add("w_pub", publisher);
            roomProps.Add("owner", socialVRPlayer.displayName);

            options.CustomRoomProperties = roomProps;
            options.CustomRoomPropertiesForLobby = new string[] { "w_name", "w_pub", "owner"};

            PhotonNetwork.CreateRoom(roomName, options);
        }

        // Runs when the player has joined the room.
        public override void OnJoinedRoom() {
            // Get world Info.
            var props = PhotonNetwork.CurrentRoom.CustomRoomProperties;
            string worldName = (string)props["w_name"];
            string worldPublisher = (string)props["w_pub"];
            string worldOwner = (string)props["owner"];

            // Start loading the world.
            worldHandler.LoadWorld(worldPublisher, worldName);
        }


    }
}