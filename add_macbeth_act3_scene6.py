#!/usr/bin/env python3
"""Add missing ACT 3 SCENE 6 to macbeth_notes_cleaned_play.json"""
import json
import os

# ACT 3 SCENE 6 - Forres. The palace. Lennox and Lord discuss Macbeth
# From https://www.shakespeare-online.com/plays/macbeth_3_6.html
ACT_3_SCENE_6 = {
    "1": {"play": "[Enter LENNOX and another Lord]", "notes": []},
    "2": {"play": "LENNOX: My former speeches have but hit your thoughts,", "notes": []},
    "3": {"play": "Which can interpret further: only, I say,", "notes": []},
    "4": {"play": "Things have been strangely borne. The gracious Duncan", "notes": []},
    "5": {"play": "Was pitied of Macbeth: marry, he was dead:", "notes": []},
    "6": {"play": "And the right-valiant Banquo walk'd too late;", "notes": []},
    "7": {"play": "Whom, you may say, if't please you, Fleance kill'd,", "notes": []},
    "8": {"play": "For Fleance fled: men must not walk too late.", "notes": []},
    "9": {"play": "Who cannot want the thought how monstrous", "notes": []},
    "10": {"play": "It was for Malcolm and for Donalbain", "notes": []},
    "11": {"play": "To kill their gracious father? damned fact!", "notes": []},
    "12": {"play": "How it did grieve Macbeth! did he not straight", "notes": []},
    "13": {"play": "In pious rage the two delinquents tear,", "notes": []},
    "14": {"play": "That were the slaves of drink and thralls of sleep?", "notes": []},
    "15": {"play": "Was not that nobly done? Ay, and wisely too;", "notes": []},
    "16": {"play": "For 'twould have anger'd any heart alive", "notes": []},
    "17": {"play": "To hear the men deny't. So that, I say,", "notes": []},
    "18": {"play": "He has borne all things well: and I do think", "notes": []},
    "19": {"play": "That had he Duncan's sons under his key--", "notes": []},
    "20": {"play": "As, an't please heaven, he shall not--they should find", "notes": []},
    "21": {"play": "What 'twere to kill a father; so should Fleance.", "notes": []},
    "22": {"play": "But, peace! for from broad words and 'cause he fail'd", "notes": []},
    "23": {"play": "His presence at the tyrant's feast, I hear", "notes": []},
    "24": {"play": "Macduff lives in disgrace: sir, can you tell", "notes": []},
    "25": {"play": "Where he bestows himself?", "notes": []},
    "26": {"play": "LORD: The son of Duncan,", "notes": []},
    "27": {"play": "From whom this tyrant holds the due of birth", "notes": []},
    "28": {"play": "Lives in the English court, and is received", "notes": []},
    "29": {"play": "Of the most pious Edward with such grace", "notes": []},
    "30": {"play": "That the malevolence of fortune nothing", "notes": []},
    "31": {"play": "Takes from his high respect: thither Macduff", "notes": []},
    "32": {"play": "Is gone to pray the holy king, upon his aid", "notes": []},
    "33": {"play": "To wake Northumberland and warlike Siward:", "notes": []},
    "34": {"play": "That, by the help of these--with Him above", "notes": []},
    "35": {"play": "To ratify the work--we may again", "notes": []},
    "36": {"play": "Give to our tables meat, sleep to our nights,", "notes": []},
    "37": {"play": "Free from our feasts and banquets bloody knives,", "notes": []},
    "38": {"play": "Do faithful homage and receive free honours:", "notes": []},
    "39": {"play": "All which we pine for now: and this report", "notes": []},
    "40": {"play": "Hath so exasperate the king that he", "notes": []},
    "41": {"play": "Prepares for some attempt of war.", "notes": []},
    "42": {"play": "LENNOX: Sent he to Macduff?", "notes": []},
    "43": {"play": "LORD: He did: and with an absolute 'Sir, not I,'", "notes": []},
    "44": {"play": "The cloudy messenger turns me his back,", "notes": []},
    "45": {"play": "And hums, as who should say 'You'll rue the time", "notes": []},
    "46": {"play": "That clogs me with this answer.'", "notes": []},
    "47": {"play": "LENNOX: And that well might", "notes": []},
    "48": {"play": "Advise him to a caution, to hold what distance", "notes": []},
    "49": {"play": "His wisdom can provide. Some holy angel", "notes": []},
    "50": {"play": "Fly to the court of England and unfold", "notes": []},
    "51": {"play": "His message ere he come, that a swift blessing", "notes": []},
    "52": {"play": "May soon return to this our suffering country", "notes": []},
    "53": {"play": "Under a hand accursed!", "notes": []},
    "54": {"play": "LORD: I'll send my prayers with him.", "notes": []},
    "55": {"play": "[Exeunt]", "notes": []},
}


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "Public", "Data", "macbeth_notes_cleaned_play.json")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "ACT 3, SCENE 6" in data:
        print("ACT 3, SCENE 6 already exists. Skipping.")
        return

    # Build new dict with scene inserted before ACT 4, SCENE 1
    new_data = {}
    for key, value in data.items():
        if key == "ACT 4, SCENE 1":
            new_data["ACT 3, SCENE 6"] = ACT_3_SCENE_6
        new_data[key] = value

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print("Added ACT 3, SCENE 6 to macbeth_notes_cleaned_play.json")


if __name__ == "__main__":
    main()
