import json
import save_data

save_json = None

def openSave() :
    global save_json
    with open("save.json", "r") as save_file:
        save_json = json.load(save_file)

    save_file.close()

def getSave() :
    return save_data.Save_data.from_dict(save_json)

def saveSave() :
    with open("savebis.json", "w") as savebis_file:
        json.dump(save_data.Save_data.toJSON(), savebis_file)

openSave()

for player in save_data.Save_data.players:
    print(player.name)
    print(player.score.highs_core)
saveSave()