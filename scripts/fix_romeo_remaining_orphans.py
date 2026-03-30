#!/usr/bin/env python3
"""Fix remaining Romeo orphan notes: ACT 3 SCENE 2 backfill; ACT 5 SCENE 3 play from
Folger line numbers; Act 4 singletons; misc cleanup."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "Public/Data/ROMEO_notes.json"

# Folger Act 5 scene 3: extract (line_no, text) from through-line numbering.
# Source: Folger Shakespeare Library read view (line numbers in margin).
FOLGER_5_3_CHUNK = r"""
Enter Paris and his Page. PARIS 2854 Give me thy torch, boy. Hence and stand aloof. 2855 Yet put it out, for I would not be seen. 2856 Under yond yew trees lay thee all along, 2857 Holding thy ear close to the hollow ground. 2858 So shall no foot upon the churchyard tread 2859 (Being loose, unfirm, with digging up of graves) 2860 But thou shalt hear it. Whistle then to me 2861 As signal that thou hear'st something approach. 2862 Give me those flowers. Do as I bid thee. Go. PAGE 2863 I am almost afraid to stand alone 2864 Here in the churchyard. Yet I will adventure. PARIS 2865 Sweet flower, with flowers thy bridal bed I strew 2866 (O woe, thy canopy is dust and stones!) 2867 Which with sweet water nightly I will dew, 2868 Or, wanting that, with tears distilled by moans. 2869 The obsequies that I for thee will keep 2870 Nightly shall be to strew thy grave and weep. 2871 The boy gives warning something doth approach. 2872 What cursed foot wanders this way tonight, 2873 To cross my obsequies and true love's rite? 2874 What, with a torch? Muffle me, night, awhile. ROMEO 2875 Give me that mattock and the wrenching iron. 2876 Hold, take this letter. Early in the morning 2877 See thou deliver it to my father's house. 2878 Give me the light. Upon thy life I charge thee, 2879 Whate'er thou hear'st or seest, stand all aloof 2880 And do not interrupt me in my course. 2881 Why I descend into this bed of death, 2882 Is partly to behold my lady's face, 2883 But chiefly to take thence from her dead finger 2884 A precious ring, a ring that I must use 2885 In dear employment. Therefore hence, begone. 2886 But if thou, jealous, dost return to pry 2887 In what I farther shall intend to do, 2888 By heaven, I will tear thee joint by joint 2889 And strew this hungry churchyard with thy limbs. 2890 The time and my intents are savage-wild, 2891 More fierce and more inexorable far 2892 Than empty tigers or the roaring sea. BALTHASAR 2893 I will be gone, sir, and not trouble you. ROMEO 2894 So shalt thou show me friendship. Take thou that. 2895 Live, and be prosperous, and farewell, good fellow. BALTHASAR 2896 For all this same, I'll hide me hereabout. 2897 His looks I fear, and his intents I doubt. ROMEO 2898 Thou detestable maw, thou womb of death, 2899 Gorged with the dearest morsel of the earth, 2900 Thus I enforce thy rotten jaws to open, 2901 And in despite I'll cram thee with more food. PARIS 2902 This is that banished haughty Montague, 2903 That murdered my love's cousin, with which grief, 2904 It is supposed the fair creature died, 2905 And here is come to do some villainous shame 2906 To the dead bodies. I will apprehend him. 2907 Stop thy unhallowed toil, vile Montague. 2908 Can vengeance be pursued further than death? 2909 Condemned villain, I do apprehend thee. 2910 Obey, and go with me, for thou must die. ROMEO 2911 I must indeed, and therefore came I hither. 2912 Good gentle youth, tempt not a desperate man. 2913 Fly hence, and leave me. Think upon these gone. 2914 Let them affright thee. I beseech thee, youth, 2915 Put not another sin upon my head 2916 By urging me to fury. O, begone! 2917 By heaven, I love thee better than myself, 2918 For I come hither armed against myself. 2919 Stay not, begone, live, and hereafter say 2920 A madman's mercy bid thee run away. PARIS 2921 I do defy thy conjurations, 2922 And apprehend thee for a felon here. ROMEO 2923 Wilt thou provoke me? Then have at thee, boy! PAGE 2924 O Lord, they fight! I will go call the watch. PARIS 2925 O, I am slain! If thou be merciful, 2926 Open the tomb, lay me with Juliet. ROMEO 2927 In faith, I will.—Let me peruse this face. 2928 Mercutio's kinsman, noble County Paris! 2929 What said my man when my betossed soul 2930 Did not attend him as we rode? I think 2931 He told me Paris should have married Juliet. 2932 Said he not so? Or did I dream it so? 2933 Or am I mad, hearing him talk of Juliet, 2934 To think it was so?—O, give me thy hand, 2935 One writ with me in sour misfortune's book! 2936 I'll bury thee in a triumphant grave.— 2937 A grave? O, no. A lantern, slaughtered youth, 2938 For here lies Juliet, and her beauty makes 2939 This vault a feasting presence full of light.— 2940 Death, lie thou there, by a dead man interred. 2941 How oft when men are at the point of death 2942 Have they been merry, which their keepers call 2943 A lightning before death! O, how may I 2944 Call this a lightning?—O my love, my wife! 2945 Death, that hath sucked the honey of thy breath, 2946 Hath had no power yet upon thy beauty. 2947 Thou art not conquered. Beauty's ensign yet 2948 Is crimson in thy lips and in thy cheeks, 2949 And death's pale flag is not advanced there.— 2950 Tybalt, liest thou there in thy bloody sheet? 2951 O, what more favor can I do to thee 2952 Than with that hand that cut thy youth in twain 2953 To sunder his that was thine enemy? 2954 Forgive me, cousin.—Ah, dear Juliet, 2955 Why art thou yet so fair? Shall I believe 2956 That unsubstantial death is amorous, 2957 And that the lean abhorred monster keeps 2958 Thee here in dark to be his paramour? 2959 For fear of that, I still will stay with thee 2960 And never from this palace of dim night 2961 Depart again. Here, here will I remain 2962 With worms that are thy chambermaids. O, here 2963 Will I set up my everlasting rest, 2964 And shake the yoke of inauspicious stars 2965 From this world-wearied flesh. Eyes, look your last. 2966 Arms, take your last embrace. And, lips, O, you 2967 The doors of breath, seal with a righteous kiss 2968 A dateless bargain to engrossing death. 2969 Come, bitter conduct, come, unsavory guide! 2970 Thou desperate pilot, now at once run on 2971 The dashing rocks thy seasick weary bark! 2972 Here's to my love. O true apothecary, 2973 Thy drugs are quick. Thus with a kiss I die. FRIAR 2974 Saint Francis be my speed! How oft tonight 2975 Have my old feet stumbled at graves!—Who's there? BALTHASAR 2976 Here's one, a friend, and one that knows you well. FRIAR 2977 Bliss be upon you. Tell me, good my friend, 2978 What torch is yond that vainly lends his light 2979 To grubs and eyeless skulls? As I discern, 2980 It burneth in the Capels' monument. BALTHASAR 2981 It doth so, holy sir, and there's my master, 2982 One that you love. FRIAR 2983 Who is it? BALTHASAR 2984 Romeo. FRIAR 2985 How long hath he been there? BALTHASAR 2986 Full half an hour. FRIAR 2987 Go with me to the vault. BALTHASAR 2988 I dare not, sir: 2989 My master knows not but I am gone hence, 2990 And fearfully did menace me with death, 2991 If I did stay to look on his intents. FRIAR 2992 Stay, then; I'll go alone. Fear comes upon me: 2993 O, much I fear some ill unlucky thing. BALTHASAR 2994 As I did sleep under this yew tree here, 2995 I dreamt my master and another fought, 2996 And that my master slew him. FRIAR 2997 Romeo! 2998 Alack, alack, what blood is this, which stains 2999 The stony entrance of this sepulcher? 3000 What mean these masterless and gory swords 3001 To lie discolored by this place of peace? 3002 Romeo! O, pale! Who else? What, Paris too? 3003 And steeped in blood? Ah, what an unkind hour 3004 Is guilty of this lamentable chance! 3005 The lady stirs. JULIET 3006 O comfortable friar, where is my lord? 3007 I do remember well where I should be, 3008 And there I am. Where is my Romeo? FRIAR 3009 I hear some noise.—Lady, come from that nest 3010 Of death, contagion, and unnatural sleep. 3011 A greater power than we can contradict 3012 Hath thwarted our intents. Come, come away. 3013 Thy husband in thy bosom there lies dead, 3014 And Paris too. Come, I'll dispose of thee 3015 Among a sisterhood of holy nuns. 3016 Stay not to question, for the watch is coming. 3017 Come, go, good Juliet, I dare no longer stay. JULIET 3018 Go, get thee hence, for I will not away. 3019 What's here? A cup closed in my true love's hand? 3020 Poison, I see, hath been his timeless end.— 3021 O churl, drunk all, and left no friendly drop 3022 To help me after? I will kiss thy lips. 3023 Haply some poison yet doth hang on them, 3024 To make me die with a restorative. 3025 Thy lips are warm! WATCH 3026 Lead, boy. Which way? JULIET 3027 Yea, noise? Then I'll be brief. O happy dagger, 3028 This is thy sheath. There rust, and let me die. PAGE 3029 This is the place, there where the torch doth burn. WATCH 3030 The ground is bloody.—Search about the churchyard. 3031 Go, some of you, whoe'er you find attach. 3032 Pitiful sight! Here lies the County slain, 3033 And Juliet bleeding, warm, and newly dead, 3034 Who here hath lain this two days buried.— 3035 Go, tell the Prince. Run to the Capulets. 3036 Raise up the Montagues. Some others search. 3037 We see the ground whereon these woes do lie, 3038 But the true ground of all these piteous woes 3039 We cannot without circumstance descry. WATCH 3040 Here's Romeo's man. We found him in the churchyard. WATCH 3041 Hold him in safety till the Prince come hither. WATCH 3042 Here is a friar that trembles, sighs, and weeps. 3043 We took this mattock and this spade from him 3044 As he was coming from this churchyard side. WATCH 3045 A great suspicion. Stay the Friar too. PRINCE 3046 What misadventure is so early up 3047 That calls our person from our morning rest? CAPULET 3048 What should it be that is so shrieked abroad? LADY 3049 O, the people in the street cry "Romeo," 3050 Some "Juliet," and some "Paris," and all run 3051 With open outcry toward our monument. PRINCE 3052 What fear is this which startles in our ears? WATCH 3053 Sovereign, here lies the County Paris slain, 3054 And Romeo dead, and Juliet, dead before, 3055 Warm and new killed. PRINCE 3056 Search, seek, and know how this foul murder comes. WATCH 3057 Here is a friar, and slaughtered Romeo's man, 3058 With instruments upon them fit to open 3059 These dead men's tombs. CAPULET 3060 O heavens! O wife, look how our daughter bleeds! 3061 This dagger hath mista'en, for, lo, his house 3062 Is empty on the back of Montague, 3063 And it mis-sheathed in my daughter's bosom. LADY 3064 O me, this sight of death is as a bell 3065 That warns my old age to a sepulcher. PRINCE 3066 Come, Montague, for thou art early up 3067 To see thy son and heir now early down. MONTAGUE 3068 Alas, my liege, my wife is dead tonight. 3069 Grief of my son's exile hath stopped her breath. 3070 What further woe conspires against mine age? PRINCE 3071 Look, and thou shalt see. MONTAGUE 3072 O thou untaught! What manners is in this, 3073 To press before thy father to a grave? PRINCE 3074 Seal up the mouth of outrage for a while, 3075 Till we can clear these ambiguities, 3076 And know their spring, their head, their true descent, 3077 And then will I be general of your woes 3078 And lead you even to death. Meantime forbear, 3079 And let mischance be slave to patience.— 3080 Bring forth the parties of suspicion. FRIAR 3081 I am the greatest, able to do least, 3082 Yet most suspected, as the time and place 3083 Doth make against me, of this direful murder. 3084 And here I stand, both to impeach and purge 3085 Myself condemned and myself excused. PRINCE 3086 Then say at once what thou dost know in this. FRIAR 3087 I will be brief, for my short date of breath 3088 Is not so long as is a tedious tale. 3089 Romeo, there dead, was husband to that Juliet, 3090 And she, there dead, that Romeo's faithful wife. 3091 I married them, and their stol'n marriage day 3092 Was Tybalt's doomsday, whose untimely death 3093 Banished the new-made bridegroom from this city, 3094 For whom, and not for Tybalt, Juliet pined. 3095 You, to remove that siege of grief from her, 3096 Betrothed and would have married her perforce 3097 To County Paris. Then comes she to me, 3098 And with wild looks bid me devise some mean 3099 To rid her from this second marriage, 3100 Or in my cell there would she kill herself. 3101 Then gave I her, so tutored by my art, 3102 A sleeping potion, which so took effect 3103 As I intended, for it wrought on her 3104 The form of death. Meantime I writ to Romeo 3105 That he should hither come as this dire night, 3106 To help to take her from her borrowed grave, 3107 Being the time the potion's force should cease. 3108 But he which bore my letter, Friar John, 3109 Was stayed by accident, and yesternight 3110 Returned my letter back. Then all alone 3111 At the prefixed hour of her waking 3112 Came I to take her from her kindred's vault, 3113 Meaning to keep her closely at my cell 3114 Till I conveniently could send to Romeo. 3115 But when I came, some minute ere the time 3116 Of her awakening, here untimely lay 3117 The noble Paris and true Romeo dead. 3118 She wakes, and I entreated her come forth, 3119 And bear this work of heaven with patience. 3120 But then a noise did scare me from the tomb, 3121 And she, too desperate, would not go with me, 3122 But, as it seems, did violence on herself. 3123 All this I know, and to the marriage 3124 Her nurse is privy. And if aught in this 3125 Miscarried by my fault, let my old life 3126 Be sacrificed some hour before his time 3127 Unto the rigor of severest law. PRINCE 3128 We still have known thee for a holy man.— 3129 Where's Romeo's man? What can he say to this? BALTHASAR 3130 I brought my master news of Juliet's death, 3131 And then in post he came from Mantua 3132 To this same place, to this same monument. 3133 This letter he early bid me give his father, 3134 And threatened me with death, going in the vault, 3135 If I departed not and left him there. PRINCE 3136 Give me the letter. I will look on it.— 3137 Where is the County's page, that raised the watch? 3138 Sirrah, what made your master in this place? PAGE 3139 He came with flowers to strew his lady's grave, 3140 And bid me stand aloof, and so I did. 3141 Anon comes one with light to ope the tomb, 3142 And by and by my master drew on him, 3143 And then I ran away to call the watch. PRINCE 3144 This letter doth make good the Friar's words, 3145 Their course of love, the tidings of her death, 3146 And here he writes that he did buy a poison 3147 Of a poor 'pothecary, and therewithal 3148 Came to this vault to die and lie with Juliet. 3149 Where be these enemies? Capulet! Montague! 3150 See what a scourge is laid upon your hate, 3151 That heaven finds means to kill your joys with love, 3152 And I, for winking at your discords too, 3153 Have lost a brace of kinsmen. All are punished. CAPULET 3154 O brother Montague, give me thy hand. 3155 This is my daughter's jointure, for no more 3156 Can I demand. MONTAGUE 3157 But I can give thee more, 3158 For I will ray her statue in pure gold, 3159 That whiles Verona by that name is known, 3160 There shall no figure at such rate be set 3161 As that of true and faithful Juliet. CAPULET 3162 As rich shall Romeo's by his lady's lie, 3163 Poor sacrifices of our enmity. PRINCE 3164 A glooming peace this morning with it brings. 3165 The sun for sorrow will not show his head. 3166 Go hence to have more talk of these sad things. 3167 Some shall be pardoned, and some punished. 3168 For never was a story of more woe 3169 Than this of Juliet and her Romeo.
"""


def normalize_play_line(s: str) -> str:
    if not s:
        return ""
    s = s.split("\n")[0].strip()
    m = re.match(r"^(Nurse)\s*:\s*(.*)$", s, re.I)
    if m:
        return f"NURSE: {m.group(2)}"
    m = re.match(r"^([A-Z][A-Z\s]+?)\s*:\s*(.*)$", s)
    if m:
        sp = " ".join(m.group(1).split())
        return f"{sp}: {m.group(2)}"
    return s


def build_act5_scene_line_map() -> dict[str, str]:
    """Variorum keys = 1-based scene line numbers; Folger through-lines 2854.. map to 1.."""
    parts = re.split(r"\s+(\d{4})\s+", FOLGER_5_3_CHUNK)
    by_folger: dict[int, str] = {}
    i = 1
    while i + 1 < len(parts):
        num = int(parts[i])
        body = parts[i + 1].strip()
        by_folger[num] = body
        i += 2
    start = 2854
    out: dict[str, str] = {}
    for fol in sorted(by_folger):
        si = fol - start + 1
        out[str(si)] = by_folger[fol]
    return out


def backfill_act3_scene2(data: dict) -> None:
    s = data["ACT 3, SCENE 2"]
    extra_1593: list = []
    if "1593" in s and s["1593"].get("notes"):
        extra_1593 = list(s["1593"]["notes"])
    if "1593" in s:
        del s["1593"]
    if "misc" in s:
        s["misc"] = {"play": "", "notes": []}
    for kk in range(1, 148):
        k = str(kk)
        if k not in s:
            continue
        ent = s[k]
        notes = list(ent.get("notes") or [])
        if not notes:
            ent["play"] = ""
            continue
        play = normalize_play_line(notes[0])
        ent["play"] = play
        notes.pop(0)
        ent["notes"] = notes
    if extra_1593:
        s.setdefault("1", {"play": "", "notes": []})
        s["1"].setdefault("notes", []).extend(extra_1593)


def backfill_act5_scene3(data: dict) -> None:
    line_map = build_act5_scene_line_map()
    s = data["ACT 5, SCENE 3"]
    for k, ent in list(s.items()):
        if not isinstance(ent, dict):
            continue
        if k not in line_map:
            continue
        play = line_map[k]
        notes = list(ent.get("notes") or [])
        ent["play"] = play
        ent["notes"] = notes


def fix_act4(data: dict) -> None:
    """Clear junk key; move Keightley Primero note onto 'set up his rest' line."""
    if "1861" in data.get("ACT 4, SCENE 3", {}):
        data["ACT 4, SCENE 3"]["1861"] = {"play": "", "notes": []}
    sc = "ACT 4, SCENE 5"
    if "1813" in data.get(sc, {}):
        notes = data[sc]["1813"].get("notes") or []
        if notes:
            data[sc].setdefault("6", {"play": "", "notes": []})
            data[sc]["6"].setdefault("notes", []).extend(notes)
        data[sc]["1813"] = {"play": "", "notes": []}


def main() -> None:
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)
    backfill_act3_scene2(data)
    backfill_act5_scene3(data)
    fix_act4(data)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("Wrote", PATH)


if __name__ == "__main__":
    main()
