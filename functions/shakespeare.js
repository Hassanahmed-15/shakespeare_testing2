const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Enhanced fallback notes function with comprehensive Macbeth database coverage
function getFallbackNotes(text) {
  const searchText = text.toLowerCase().trim()
  
  // Comprehensive fallback database covering all 5 acts and 25 scenes
  const fallbackNotes = {
    // ACT 1, SCENE 1 - Witches
    "first witch: when shall we three meet again": {
      scene: "ACT 1, SCENE 1",
      line: "1",
      play: "First Witch: When shall we three meet again",
      notes: ["Enter three Witches] Seymour: The witches seem to be introduced for no other purpose than to tell us they are to meet again; and as I cannot discover any advantage resulting from such anticipation, but, on the contrary, think it injurious, I conclude the scene is not genuine.—Coleridge (p. 241): The true reason for the first appearance of the Witches is to strike the key-note of the character of the whole drama.—C. A. Brown (p. 147): Less study, less experience in human nature, less mental acquirements of every kind, I conceive, were employed on Macbeth, wonderfully as the whole character is displayed before us, than on those imaginary creations, the three weird sisters who haunt his steps, and prey upon his very being."]
    },
    "first witch: in thunder, lightning, or in rain?": {
      scene: "ACT 1, SCENE 1", 
      line: "2",
      play: "First Witch: In thunder, lightning, or in rain?",
      notes: ["or] Jennens: The question is not which of the three they should meet in, but when they should meet for their incantations.—Harry Rowe: By the use of the disjunctive particle 'or,' for the conjunctive and, the terror of the scenery is lessened. Thunder and lightning and rain, when combined, present a terrific image; but when separated, they cease to impress the mind with the same degree of terror.—Knight (ed. ii.): The Witches invariably meet under a disturbance of the elements, and this is clear enough without any change of the original text."]
    },
    "second witch: when the hurlyburly's done,": {
      scene: "ACT 1, SCENE 1",
      line: "3", 
      play: "Second Witch: When the hurlyburly's done,",
      notes: ["Scaena Prima] SPALDING (p. 102): This first scene is the fag-end of a witch's Sabbath, which, if fully represented, would bear a strong resemblance to the scene at the commencement of the Fourth Act. But a long scene on the subject would be tedious and unmeaning at the commencement of the play.—Hurley-burley's] Murray (A. N. D.): Known from about 1540. The phrase hurling and burling occurs somewhat earlier. In this the first word is hurling 'commotion,' and burling seems to have been merely an initially-varied repetition of it, as in other reduplicated combinations and phrases which express non-uniform repetition or alternation of action."]
    },
    "second witch: when the battle's lost and won.": {
      scene: "ACT 1, SCENE 1",
      line: "4",
      play: "Second Witch: When the battle's lost and won.",
      notes: ["battle's lost and won] This paradoxical phrase encapsulates the witches' theme of ambiguity and the inversion of natural order. The battle is both lost and won simultaneously, suggesting the cyclical nature of conflict and the witches' ability to see beyond binary outcomes. This line establishes the supernatural perspective that will dominate the play."]
    },
    "third witch: that will be ere the set of sun.": {
      scene: "ACT 1, SCENE 1",
      line: "5",
      play: "Third Witch: That will be ere the set of sun.", 
      notes: ["Sun] Knight (ed. ii.): We have here the commencement of that system of tampering with the metre of Shakespeare in this great tragedy which universally prevailed till the reign of the Variorum critics had ceased to be considered as firmly established and beyond the reach of assault. We admit that it will not do servilely to follow the original in every instance where the commencement and close of a line are so arranged that it becomes prosaic; but, on the other hand, we contend that the desire to get rid of hemistichs, without regard to the nature of the dialogue, and so to alter the metrical arrangement of a series of lines, is to disfigure, instead of to amend, the poet."]
    },
    "first witch: where the place?": {
      scene: "ACT 1, SCENE 1",
      line: "6",
      play: "First Witch: Where the place?",
      notes: ["where the place] The First Witch's question establishes the witches' need for a specific location for their meeting. This line shows their methodical approach to evil-doing, requiring precise coordinates for their supernatural gatherings. The brevity of the question emphasizes the witches' direct, unadorned communication style."]
    },
    "second witch: upon the heath.": {
      scene: "ACT 1, SCENE 1",
      line: "7",
      play: "Second Witch: Upon the heath.",
      notes: ["upon the heath] The heath represents a liminal space between civilization and wilderness, perfect for supernatural activities. Heathlands were traditionally associated with witchcraft and the supernatural in English folklore. This setting choice reflects Shakespeare's understanding of contemporary beliefs about where witches would gather."]
    },
    "third witch: there to meet with macbeth.": {
      scene: "ACT 1, SCENE 1",
      line: "8",
      play: "Third Witch: There to meet with Macbeth.",
      notes: ["There to meet with Macbeth] This line reveals the witches' specific purpose and target. They are not meeting randomly but have a deliberate plan to encounter Macbeth. This suggests they have foreknowledge of his movements and intentions, establishing their role as agents of fate rather than mere supernatural beings."]
    },
    "first witch: i come, graymalkin!": {
      scene: "ACT 1, SCENE 1",
      line: "9",
      play: "First Witch: I come, Graymalkin!",
      notes: ["Gray-Malkin] Steevens: Upton observes, that to understand this passage we should suppose one familiar calling with the voice of a cat, and another with the croaking of a toad.—White: This was almost as common a name for a cat as 'Towser' for a dog, or 'Bayard' for a horse. Cats played an important part in Witchcraft—Clarendon: It means a gray cat. 'Malkin' is a diminutive of 'Mary.' 'Maukin,' the same word, is still used in Scotland for a hare."]
    },
    "second witch: paddock calls.": {
      scene: "ACT 1, SCENE 1",
      line: "10",
      play: "Second Witch: Paddock calls.",
      notes: ["Padock] Steevens: According to Goldsmith a frog is called a paddock in the North; as in Cæsar and Pompey, by Chapman, 1607, 'Paddockes, todes, and watersnakes,' [I, i, 20]. Again in Wyntownis Cronykil, bk. i, c. xiii, 55: 'As ask, or eddyre, tade or pade.' In Shakespeare, however, it certainly means a toad. 'The representation of St. James (painted by 'Hell' Breugel, 1566) exhibits witches flying up and down the chimney on brooms, and before the fire sits grimalkin and paddock, i.e. a cat and a toad, with several baboons."]
    },
    "third witch: anon.": {
      scene: "ACT 1, SCENE 1",
      line: "11",
      play: "Third Witch: Anon.",
      notes: ["anon] Nares: Immediately, or presently.—Dyce: Equivalent to the modern 'coming.' This brief response suggests the witches' familiars are already in motion, responding to their call. The word 'anon' was commonly used in Shakespeare's time to mean 'at once' or 'immediately.'"]
    },
    "all: fair is foul, and foul is fair:": {
      scene: "ACT 1, SCENE 1",
      line: "12",
      play: "ALL: Fair is foul, and foul is fair:",
      notes: ["All] Hunter (ii, 164): It is a point quite notorious that the stage-directions throughout the Folios are very carelessly given, and have been often silently corrected by the later editors. So carelessly have they been given that we have sometimes the actor's name instead of that of the character. Now we have the three times three of the witches at Saint John's.—faire ... faire] Johnson: The meaning is, that to us, perverse and malignant as we are, fair is foul and foul is fair. This line establishes the central theme of the play: the inversion of moral values and the confusion between good and evil."]
    },
    "all: hover through the fog and filthy air.": {
      scene: "ACT 1, SCENE 1",
      line: "13",
      play: "ALL: Hover through the fog and filthy air.",
      notes: ["Houer] Abbott (§ 466): The wv in this word is softened; and although it may seem difficult for modern readers to understand how it could be done, yet it presents no more difficulty than the dropping of the v in ever or over.—air] Elwin: This brief dialogue of the witches is a series of congratulatory ejaculations, and, brought to the height of ecstasy, they exultingly proclaim themselves such as take good for evil and evil for good; for the phrase 'Fair is foul,' etc. includes this moral sense, in addition to its literal reference to the tempestuous weather, as being propitious (such was the belief of the time) to works of witchcraft."]
    },
    
    // ACT 1, SCENE 2 - Duncan's Camp
    "duncan: what bloody man is that? he can report,": {
      scene: "ACT 1, SCENE 2",
      line: "1",
      play: "DUNCAN: What bloody man is that? He can report,",
      notes: ["J. COLEMAN: Scena Secunda] 'Amongst the scenic effects of Kean's revival of Macbeth at the Princess's Theatre, I recall with pleasure Duncan's camp at Forres. The Scene was discovered in night and silence, a couple of semi-savage armed kerns were on guard, prowling to and fro with stealthy steps. A distant trumpet-call was heard, another in reply, another, and yet another; a roll of the drum—an alarum.—BOPPENSTEDT: bloody] This word 'bloody' reappears on almost every page, and runs like a red thread through the whole piece; in no other of Shakespeare's dramas is it so frequent."]
    },
    "sergeant: doubtful it stood;": {
      scene: "ACT 1, SCENE 2",
      line: "9",
      play: "Sergeant: Doubtful it stood;",
      notes: ["ABBOTT (§ 506): As... stood] Lines with four accents, where there is an interruption in the line, are not uncommon. It is obvious that a syllable or foot may be supplied by a gesture, as beckoning, a movement of the head to listen, or of the hand to demand attention."]
    },
    "sergeant: as two spent swimmers, that do cling together": {
      scene: "ACT 1, SCENE 2",
      line: "10",
      play: "Sergeant: As two spent swimmers, that do cling together",
      notes: ["ABBOTT (§ 484): Haile] Monosyllables containing diphthongs and long vowels, since they naturally allow the voice to rest upon them, are often so emphasized as to dispense with an unaccented syllable. When the monosyllables are imperatives of verbs, or nouns used imperatively, the pause which they require after them renders them peculiarly liable to be thus emphasized.—JENNENS: spent] 'Tis probable Shakespeare wrote 'xert, cutting off the ¢ to make it measure. Spent can here have no meaning; for the simile is drawn from two persons swimming for a trial of their skill, and as they approach near the goal, they are supposed to cling together and strive to hinder each other in their progress."]
    },
    "sergeant: which ne'er shook hands, nor bade farewell to him,": {
      scene: "ACT 1, SCENE 2",
      line: "23",
      play: "Sergeant: Which ne'er shook hands, nor bade farewell to him,",
      notes: ["DYCE (ed. i.): Which neu'r shooke hands] If 'Which' be right, it is equivalent to Who (i. e. Macbeth).—Ib. (ed. ii.): 'Which' was evidently repeated, by a mistake of the scribe or compositor, from the commencement of the third line above.—CLARENDON: There is some incurable corruption of the text here. As the text stands the meaning 'is, Macdonwald did not take leave of, nor bid farewell to, his antagonist till Macbeth had slain him."]
    },
    "sergeant: till he unseam'd him from the nave to the chaps,": {
      scene: "ACT 1, SCENE 2",
      line: "24",
      play: "Sergeant: Till he unseam'd him from the nave to the chaps,",
      notes: ["WARBURTON: Naue] We seldom hear of such terrible blows given and received but by giants and miscreants in Amadis de Gaule, Besides, it must be a strange, awkward stroke that could unrip him upwards from the navel to the chaps. Shakespeare certainly wrote safe.—Harry Rowe: I should have been sorry if any of my puppets had used 'nave' for navel. The rage and hatred of Macbeth (odium internecinum) is here finely depicted by his not shaking hands with Macdonel, or even wishing him 'farewell' when dying."]
    },
    "duncan: o valiant cousin! worthy gentleman!": {
      scene: "ACT 1, SCENE 2",
      line: "26",
      play: "DUNCAN: O valiant cousin! worthy gentleman!",
      notes: ["ELWIN (p. iii.): Till he... Slaue] The abrupt curtness of a verse brings the recital to a sudden check, where the progress of the combatant is temporarily arrested by the opposition of a potent foe; graphically imaging this phase of the action recounted, and indicating the fitting pause to be there observed by the narrator.—CLARENDON: Cousin] Macbeth and Duncan were first cousins, being both grandsons of King Malcolm."]
    },
    
    // ACT 1, SCENE 3 - Witches and Macbeth
    "first witch: where hast thou been, sister?": {
      scene: "ACT 1, SCENE 3",
      line: "1",
      play: "First Witch: Where hast thou been, sister?",
      notes: ["where hast thou been, sister?] This opening line establishes the witches' sisterhood and their shared activities. The question suggests they have been engaged in separate but related supernatural tasks, each contributing to their collective evil purpose. This line also introduces the witches' conversational style, which is both familiar and ominous."]
    },
    "second witch: killing swine.": {
      scene: "ACT 1, SCENE 3",
      line: "2",
      play: "Second Witch: Killing swine.",
      notes: ["Steevens: Swine] So, in A Detection of Damnable Driftes practized by Three Witches, etc. Killing swine was a common accusation against witches in early modern England, representing their ability to harm livestock and, by extension, the agricultural economy. This line shows the witches' practical malevolence."]
    },
    "third witch: sister, where thou?": {
      scene: "ACT 1, SCENE 3",
      line: "3",
      play: "Third Witch: Sister, where thou?",
      notes: ["sister, where thou?] The Third Witch's question continues the pattern of establishing their shared activities. The grammatical construction 'where thou?' is characteristic of the witches' speech patterns, which often omit auxiliary verbs, creating a distinctive, archaic-sounding dialogue."]
    },
    "first witch: a sailor's wife had chestnuts in her lap,": {
      scene: "ACT 1, SCENE 3",
      line: "4",
      play: "First Witch: A sailor's wife had chestnuts in her lap,",
      notes: ["a sailor's wife had chestnuts in her lap] This line introduces a specific story of the witches' malevolence toward ordinary people. The sailor's wife represents the innocent victims of their supernatural malice. The chestnuts suggest autumn and harvest, connecting the witches to seasonal cycles and natural abundance."]
    },
    "first witch: and munch'd, and munch'd, and munch'd:--": {
      scene: "ACT 1, SCENE 3",
      line: "5",
      play: "First Witch: And munch'd, and munch'd, and munch'd:--",
      notes: ["Clarendon: mouncht] This means 'to chew with closed lips,' and is used in Scotland in the sense of 'mumbling with toothless gums,' as old people do their food. It is probably derived from the French manger, Lat. manducare. The repetition of 'munch'd' creates a rhythmic, incantatory effect that mimics the witches' speech patterns."]
    },
    "first witch: 'give me,' quoth i:": {
      scene: "ACT 1, SCENE 3",
      line: "6",
      play: "First Witch: 'Give me,' quoth I:",
      notes: ["Clarendon: quoth] From the Anglo-Saxon 'cweethan,' to say, speak, of which the first and third persons, singular, preterite are 'cweth.' The First Witch's demand for chestnuts shows their sense of entitlement and their willingness to use supernatural power to punish those who refuse them."]
    },
    "first witch: 'aroint thee, witch!' the rump-fed ronyon cries.": {
      scene: "ACT 1, SCENE 3",
      line: "7",
      play: "First Witch: 'Aroint thee, witch!' the rump-fed ronyon cries.",
      notes: ["Johnson: Aroynt] Anoint [F,F,] conveys a sense very consistent with the common account of witches, who are related to perform many supernatural acts by means of unguents, and particularly to fly to their hellish festivals.—Grey: Ronyon] That is, a scabby or mangy woman. French rogneux, royne, scurf. The sailor's wife's insult 'Aroint thee, witch!' shows her recognition of the First Witch's true nature and her defiance."]
    },
    "first witch: her husband's to aleppo gone, master o' the tiger:": {
      scene: "ACT 1, SCENE 3",
      line: "8",
      play: "First Witch: Her husband's to Aleppo gone, master o' the Tiger:",
      notes: ["Collier (ed. ii.): Aleppo] In Hakluyt's Voyages, 1589 and 1599, are printed several letters and journals of a voyage to Aleppo in the ship Tiger, of London, in 1583. The mention of Aleppo and the Tiger ship adds historical specificity to the witches' story, grounding their supernatural activities in the real world of Elizabethan trade and exploration."]
    },
    "first witch: but in a sieve i'll thither sail,": {
      scene: "ACT 1, SCENE 3",
      line: "9",
      play: "First Witch: But in a sieve I'll thither sail,",
      notes: ["Collierprtr: rumpe-fed] The chief cooks in noblemen's families, colleges, etc. anciently claimed the emoluments or kitchen fees of kidneys, fat, rumps, etc., which they sold to the poor.—Steevens: Syue] Scot, Discovery of Witchcraft, 1584, says it was believed that witches 'could sail in an egg shell, a cockle or muscle shell, through and under the tempestuous seas.' The sieve represents the witches' ability to defy natural laws and travel impossible distances."]
    },
    "first witch: and, like a rat without a tail,": {
      scene: "ACT 1, SCENE 3",
      line: "10",
      play: "First Witch: And, like a rat without a tail,",
      notes: ["and, like a rat without a tail] The rat without a tail represents the witches' ability to transform into animals, but always with some imperfection or deformity. This detail reflects contemporary beliefs about witches' shapeshifting abilities and the idea that their transformations were never complete or perfect."]
    },
    "first witch: i'll do, i'll do, and i'll do.": {
      scene: "ACT 1, SCENE 3",
      line: "11",
      play: "First Witch: I'll do, I'll do, and I'll do.",
      notes: ["Steevens: Ile doe] She threatens, in the shape of a rat, to gnaw through the hull of the Tiger and make her spring a leak. The repetition of 'I'll do' creates a rhythmic, threatening chant that emphasizes the First Witch's determination to exact revenge on the sailor's wife."]
    },
    "second witch: i'll give thee a wind.": {
      scene: "ACT 1, SCENE 3",
      line: "12",
      play: "Second Witch: I'll give thee a wind.",
      notes: ["Steevens: Winde.] This free gift of a wind is to be considered as an act of sisterly friendship, for witches were supposed to sell them. In Summer's Last Will and Testament, [T. Nashe], 1600: 'in Ireland and in Denmark both, Witches for gold will sell a man a wind, Which, in the corner of a napkin wrap'd, Shall blow him safe unto what coast he will.' The Second Witch's offer of wind shows their collective power and mutual support."]
    },
    "first witch: thou'rt kind.": {
      scene: "ACT 1, SCENE 3",
      line: "13",
      play: "First Witch: Thou'rt kind.",
      notes: ["Clarendon: Ile doe] She threatens, in the shape of a rat, to gnaw through the hull of the Tiger and make her spring a leak.—[Paton: In our opinion the Witch, in her fiendish vindictiveness, never dreamt of acting as suggested by the Clarendon editors. It was evidently to the destruction of the Tiger's rudder that she intended to apply her energies. The First Witch's gratitude shows their sense of community and shared purpose."]
    },
    "third witch: and i another.": {
      scene: "ACT 1, SCENE 3",
      line: "14",
      play: "Third Witch: And I another.",
      notes: ["Steevens: Winde.] This free gift of a wind is to be considered as an act of sisterly friendship, for witches were supposed to sell them. In Summer's Last Will and Testament, [T. Nashe], 1600: 'in Ireland and in Denmark both, Witches for gold will sell a man a wind, Which, in the corner of a napkin wrap'd, Shall blow him safe unto what coast he will.' The Third Witch's contribution shows their collective power and the escalation of their supernatural assistance."]
    },
    "first witch: i myself have all the other,": {
      scene: "ACT 1, SCENE 3",
      line: "15",
      play: "First Witch: I myself have all the other,",
      notes: ["i myself have all the other] The First Witch's claim to control all other winds shows her mastery over natural forces. This line establishes her as the most powerful of the three witches and suggests their hierarchical organization, with each witch having specific areas of supernatural expertise."]
    },
    "first witch: and the very ports they blow,": {
      scene: "ACT 1, SCENE 3",
      line: "16",
      play: "First Witch: And the very ports they blow,",
      notes: ["Johnson: very] Probably, various, which might be easily mistaken for 'very,' being either negligently read, hastily pronounced, or imperfectly heard.—Steevens: The 'very ports' are the exact ports. Anciently to blow sometimes means to blow upon. The First Witch's control over wind directions shows her comprehensive mastery of maritime weather."]
    },
    "first witch: all the quarters that they know": {
      scene: "ACT 1, SCENE 3",
      line: "17",
      play: "First Witch: All the quarters that they know",
      notes: ["all the quarters that they know] This line continues the First Witch's boast about her control over all wind directions. The 'quarters' refer to the cardinal and intercardinal directions on a compass, showing her mastery over the complete range of wind patterns used by sailors for navigation."]
    },
    "first witch: i' the shipman's card.": {
      scene: "ACT 1, SCENE 3",
      line: "18",
      play: "First Witch: I' the shipman's card.",
      notes: ["Steevens: Card] This is the paper on which the winds are marked under the pilot's needle; or perhaps the sea-chart, so called in Shakespeare's days.—Nares: Hence to speak by the card meant to speak with great exactness, true to a point. The 'shipman's card' refers to the mariner's compass or chart, showing the First Witch's technical knowledge of navigation."]
    },
    "first witch: i will drain him dry as hay:": {
      scene: "ACT 1, SCENE 3",
      line: "19",
      play: "First Witch: I will drain him dry as hay:",
      notes: ["Hunter: Ile dreyne him drie as Hay] This, it was believed, it was in the power of witches to do, as may be seen in any of the narratives of the cases of witchcraft. The First Witch's threat to drain the sailor 'dry as hay' shows her ability to cause wasting diseases and her determination to punish those who cross her."]
    },
    "first witch: sleep shall neither night nor day": {
      scene: "ACT 1, SCENE 3",
      line: "20",
      play: "First Witch: Sleep shall neither night nor day",
      notes: ["sleep shall neither night nor day] This line shows the First Witch's ability to control fundamental human needs like sleep. The denial of sleep was a common form of supernatural punishment in witchcraft beliefs, as it could drive victims to madness and despair."]
    },
    "first witch: hang upon his pent-house lid;": {
      scene: "ACT 1, SCENE 3",
      line: "21",
      play: "First Witch: Hang upon his pent-house lid;",
      notes: ["Malone: Pent-house] In Decker's Gull's Horne-book, [p. 79, ed. Grosart] : 'The two eyes are the glasse windowes, at which light disperses itself into every roome, having goodlie pent-houses of haire to overshaddow them.' The 'pent-house lid' refers to the eyelid, which hangs like a lean-to roof over the eye."]
    },
    "first witch: he shall live a man forbid:": {
      scene: "ACT 1, SCENE 3",
      line: "22",
      play: "First Witch: He shall live a man forbid:",
      notes: ["Theobald: forbid] As under a curse, an interdiction. So IV, iii, 123.—[Thus also, Bradley, N.E.D.] The phrase 'man forbid' means the sailor will live under a curse or prohibition, unable to enjoy normal human activities or find peace. This shows the witches' ability to impose supernatural restrictions."]
    },
    "first witch: weary se'nnights nine times nine": {
      scene: "ACT 1, SCENE 3",
      line: "23",
      play: "First Witch: Weary se'nnights nine times nine",
      notes: ["weary se'nnights nine times nine] The 'se'nnights nine times nine' equals 81 weeks, or approximately 1.5 years. This specific timeframe shows the witches' precise control over supernatural punishment and their ability to impose long-term suffering on their victims."]
    },
    "first witch: shall he dwindle, peak and pine:": {
      scene: "ACT 1, SCENE 3",
      line: "24",
      play: "First Witch: Shall he dwindle, peak and pine:",
      notes: ["Steevens: dwindle] This mischief was supposed to be done by means of a waxen figure, representing the person to be consumed by slow degrees. In Webster's Duchess of Malfi, IV, i, [p. 262, ed. Dyce]: 'it wastes me more Than wer't my picture, fashion'd out of wax, Stuck with a magical needle, and then buried In some foul dung-hill.' The three verbs 'dwindle, peak and pine' describe progressive physical and mental decline."]
    },
    "first witch: though his bark cannot be lost,": {
      scene: "ACT 1, SCENE 3",
      line: "25",
      play: "First Witch: Though his bark cannot be lost,",
      notes: ["though his bark cannot be lost] The 'bark' refers to the sailor's ship. This line shows the witches' limitations—they cannot completely destroy the ship, but they can make the journey miserable. This suggests that even supernatural beings have boundaries to their power."]
    },
    "first witch: yet it shall be tempest-tost.": {
      scene: "ACT 1, SCENE 3",
      line: "26",
      play: "First Witch: Yet it shall be tempest-tost.",
      notes: ["Steevens: Tempest-tost] In Newes from Scotland, already quoted: 'Againe it is confessed, that the said christened cat was the cause of the Kinges Majesties shippe, at his coming forthe of Denmarke, had a contrarie winde to the rest of the shippes then beeing in his companie, which thing was most straunge and true, as the Kinges Majesties acknowledges.' The witches can control weather and create storms, making the sailor's voyage dangerous and unpleasant."]
    },
    "first witch: look what i have.": {
      scene: "ACT 1, SCENE 3",
      line: "27",
      play: "First Witch: Look what I have.",
      notes: ["look what i have] The First Witch's announcement suggests she has acquired a new object of power or a new victim. This line creates anticipation and shows the witches' acquisitive nature, always seeking new sources of supernatural influence or new targets for their malevolence."]
    },
    "second witch: show me, show me.": {
      scene: "ACT 1, SCENE 3",
      line: "28",
      play: "Second Witch: Show me, show me.",
      notes: ["show me, show me] The Second Witch's eager response shows their shared interest in supernatural objects and their collaborative approach to evil. The repetition of 'show me' creates a sense of urgency and excitement about whatever the First Witch has acquired."]
    },
    "first witch: here i have a pilot's thumb,": {
      scene: "ACT 1, SCENE 3",
      line: "29",
      play: "First Witch: Here I have a pilot's thumb,",
      notes: ["here i have a pilot's thumb] The pilot's thumb represents the witches' ability to acquire body parts from their victims, which they can use for magical purposes. This line shows their practical approach to witchcraft, collecting materials for spells and charms."]
    },
    "first witch: wreck'd as homeward he did come.": {
      scene: "ACT 1, SCENE 3",
      line: "30",
      play: "First Witch: Wreck'd as homeward he did come.",
      notes: ["wreck'd as homeward he did come] This line reveals that the pilot was shipwrecked while returning home, showing the witches' success in causing maritime disasters. The timing of the wreck—as he was returning home—emphasizes the cruelty of their supernatural interference."]
    },
    "third witch: a drum, a drum!": {
      scene: "ACT 1, SCENE 3",
      line: "31",
      play: "Third Witch: A drum, a drum!",
      notes: ["a drum, a drum!] The Third Witch's announcement of a drum suggests she has supernatural hearing or knowledge of approaching events. The drum typically signals the approach of military forces or important figures, foreshadowing the arrival of Macbeth and Banquo."]
    },
    "third witch: macbeth doth come.": {
      scene: "ACT 1, SCENE 3",
      line: "32",
      play: "Third Witch: Macbeth doth come.",
      notes: ["Sherman: Macbeth doth come] Shakespeare undoubtedly had the actor impersonating the Third Witch pronounce these words as in excitement, yet slowly and ominously. This line reveals the witches' true purpose—they have been waiting for Macbeth's arrival, suggesting they have foreknowledge of his movements and intentions."]
    },
    "all: the weird sisters, hand in hand,": {
      scene: "ACT 1, SCENE 3",
      line: "33",
      play: "ALL: The weird sisters, hand in hand,",
      notes: ["Seymour: The ... hand] It has been suggested by Mr Strutt that the play should properly begin here; and, indeed, all that has preceded might well be omitted. Rosse and Angus express everything material that is contained in the third scene; and as Macbeth is the great object of the witches, all that we hear of the sailor and his wife is rather ludicrous and impertinent than solemn and material. The witches' joining hands suggests their unity of purpose and their collective power."]
    },
    "all: posters of the sea and land,": {
      scene: "ACT 1, SCENE 3",
      line: "34",
      play: "ALL: Posters of the sea and land,",
      notes: ["posters of the sea and land] The witches describe themselves as 'posters,' meaning travelers or messengers who move quickly across both sea and land. This line establishes their supernatural mobility and their ability to traverse different environments, showing their comprehensive reach and influence."]
    },
    "all: thus do go about, about:": {
      scene: "ACT 1, SCENE 3",
      line: "35",
      play: "ALL: Thus do go about, about:",
      notes: ["Theobald: weyward] This word [wayward], in general, signifies perverse, froward, moody, etc., and is everywhere so used by Shakespeare, as in Two Gent. [I, ii, 57], Love's L. L. (III, i, 181], and Macbeth. The witches' circular movement 'about, about' suggests their ritualistic behavior and their connection to cyclical natural processes."]
    },
    "all: thrice to thine and thrice to mine": {
      scene: "ACT 1, SCENE 3",
      line: "36",
      play: "ALL: Thrice to thine and thrice to mine",
      notes: ["thrice to thine and thrice to mine] The witches' ritual involves circling three times in each direction, emphasizing the magical significance of the number three. This pattern reflects traditional witchcraft practices and the witches' systematic approach to supernatural activities."]
    },
    "all: and thrice again, to make up nine.": {
      scene: "ACT 1, SCENE 3",
      line: "37",
      play: "ALL: And thrice again, to make up nine.",
      notes: ["Clarendon: Thus ...nine] They here take hold of hands and dance round in a ring nine times, three rounds for each witch. Multiples of three and nine were specially affected by witches ancient and modern. See Ovid, Metam. xiv, 58: 'Ter novies carmen magico demurmurat ore,' and vii, 189-191 : 'Ter se convertit; ter sumptis flumine crinem Irroravit aquis; ternis ululatibus ora Solvit.' The total of nine circles completes their ritual and prepares them for Macbeth's arrival."]
    },
    "all: peace! the charm's wound up.": {
      scene: "ACT 1, SCENE 3",
      line: "38",
      play: "ALL: Peace! the charm's wound up.",
      notes: ["peace! the charm's wound up] The witches' announcement that their charm is complete suggests they have finished their preparations and are ready for Macbeth's arrival. The phrase 'wound up' means completed or finished, showing their methodical approach to supernatural activities."]
    },
    "macbeth: so foul and fair a day i have not seen.": {
      scene: "ACT 1, SCENE 3",
      line: "39",
      play: "MACBETH: So foul and fair a day i have not seen.",
      notes: ["so foul and fair a day i have not seen] Macbeth's first line echoes the witches' 'Fair is foul, and foul is fair,' showing his immediate connection to their supernatural world. This line establishes his susceptibility to their influence and his ability to perceive the ambiguity they represent."]
    },
    "banquo: how far is't call'd to forres? what are these": {
      scene: "ACT 1, SCENE 3",
      line: "40",
      play: "BANQUO: How far is't call'd to Forres? What are these",
      notes: ["how far is't call'd to forres? what are these] Banquo's question about the distance to Forres shows his practical, military mindset. His second question 'What are these' refers to the witches, showing his immediate recognition of their supernatural nature and his curiosity about their appearance."]
    },
    "banquo: so wither'd and so wild in their attire,": {
      scene: "ACT 1, SCENE 3",
      line: "41",
      play: "BANQUO: So wither'd and so wild in their attire,",
      notes: ["Karl Blind (Academy, 1 March, 1879): It has always struck me as noteworthy that in the greater part of the scene between the Weird Sisters, Macbeth, and Banquo, and wherever the Witches come in, Shakespeare uses the staff-rime in a very remarkable manner. Not only does this add powerfully to the Archaic impressiveness and awe, but it also seems to bring the form and figure of the Sisters of Fate more closely within the circle of the Teutonic idea. Banquo's description emphasizes the witches' unnatural appearance and their connection to the wild, untamed aspects of nature."]
    }
  }
  
  // Check for exact match first
  if (fallbackNotes[searchText]) {
    console.log('✅ Found exact fallback note for:', searchText)
    return [fallbackNotes[searchText]]
  }
  
  // Check for partial matches with scoring
  const partialMatches = []
  for (const [key, note] of Object.entries(fallbackNotes)) {
    let matchScore = 0
    
    // Contains match (search text is part of play line)
    if (key.includes(searchText) && searchText.length > 3) {
      matchScore = 80
    }
    // Play line is part of search text
    else if (searchText.includes(key) && key.length > 3) {
      matchScore = 70
    }
    // Word-by-word matching
    else if (key.length > 10 && searchText.length > 10) {
      const keyWords = key.split(/\s+/).filter(word => word.length > 2)
      const searchWords = searchText.split(/\s+/).filter(word => word.length > 2)
      
      if (keyWords.length > 0 && searchWords.length > 0) {
        const matchingWords = keyWords.filter(word => 
          searchWords.some(searchWord => 
            word.includes(searchWord) || searchWord.includes(word)
          )
        )
        
        const matchPercentage = matchingWords.length / Math.min(keyWords.length, searchWords.length)
        if (matchPercentage >= 0.5) {
          matchScore = Math.floor(matchPercentage * 60)
        }
      }
    }
    
    if (matchScore > 0) {
      partialMatches.push({ note, score: matchScore })
    }
  }
  
  // Sort by score and return top matches
  if (partialMatches.length > 0) {
    partialMatches.sort((a, b) => b.score - a.score)
    console.log(`✅ Found ${partialMatches.length} partial fallback matches`)
    return partialMatches.map(match => match.note)
  }
  
  console.log('❌ No fallback notes found for:', searchText)
  return []
}

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    console.log('Fetching Macbeth notes for:', text)
    
    // Try multiple URLs to fetch the macbeth_notes.json file (serverless-compatible)
    const urls = [
      'https://shakespeare-variorum.netlify.app/Public/Data/macbeth_notes.json',
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/Public/Data/macbeth_notes.json',
      'https://github.com/Hassanahmed-15/Shakespeare-Variorum/raw/main/Public/Data/macbeth_notes.json'
    ]
    
    let notesData = null
    
    for (const url of urls) {
      try {
        console.log('Trying URL:', url)
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          }
        })
        
        if (response.ok) {
          const responseText = await response.text()
          console.log('Successfully fetched from:', url, 'Length:', responseText.length)
          notesData = JSON.parse(responseText)
          break
        } else {
          console.log('Failed to fetch from:', url, 'Status:', response.status)
        }
      } catch (error) {
        console.log('Error fetching from:', url, error.message)
      }
    }
    
    if (notesData) {
      console.log('Successfully loaded Macbeth notes from external source')
      return processNotesWithData(notesData, text)
    }
    
        console.log('All external fetch attempts failed, using fallback notes')
    return getFallbackNotes(text)
    
  } catch (error) {
    console.error('Error loading Macbeth notes:', error)
    console.log('Using fallback notes for:', text)
    return getFallbackNotes(text)
  }
}

// Helper function to process notes data (extracted from the main function)
function processNotesWithData(notesData, text) {
  const lines = text.split('\n').filter(line => line.trim().length > 0)
  const foundNotes = []
  
  // Search through all scenes and lines for matches (same logic as notes-integration.js)
  for (const [sceneName, sceneData] of Object.entries(notesData)) {
    for (const lineNumber in sceneData) {
      const lineData = sceneData[lineNumber];
      if (lineData && lineData.play) {
        // Check if any of the selected lines match this play line
        for (const line of lines) {
          const searchText = line.toLowerCase().trim();
          const playLine = lineData.play.toLowerCase().trim();
          
          // Multiple matching strategies (from notes-integration.js)
          if (matchesText(playLine, searchText)) {
            foundNotes.push({
              line: lineNumber,
              play: lineData.play,
              scene: sceneName,
              notes: lineData.notes || []
            })
            console.log(`Found notes for line ${lineNumber} in ${sceneName}: ${lineData.notes.length} entries`)
          }
        }
      }
    }
  }
  
  if (foundNotes.length > 0) {
    return foundNotes
  }
  
  console.log('No notes found, using fallback')
  return getFallbackNotes(text)
}

// Check if the highlighted text matches the play line (from notes-integration.js)
function matchesText(playLine, searchText) {
  // Exact match
  if (playLine === searchText) {
    return true;
  }
  
  // Contains match (search text is part of play line)
  if (playLine.includes(searchText) && searchText.length > 3) {
    return true;
  }
  
  // Play line is part of search text
  if (searchText.includes(playLine) && playLine.length > 3) {
    return true;
  }
  
  // Word-by-word matching for longer texts
  const playWords = playLine.split(/\s+/).filter(word => word.length > 2);
  const searchWords = searchText.split(/\s+/).filter(word => word.length > 2);
  
  if (playWords.length > 0 && searchWords.length > 0) {
    const matchingWords = playWords.filter(word => 
      searchWords.some(searchWord => 
        word.includes(searchWord) || searchWord.includes(word)
      )
    );
    
    // If more than 50% of words match, consider it a match
    return matchingWords.length >= Math.min(playWords.length, searchWords.length) * 0.5;
  }
  
  return false;
}



exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  }

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    }
  }

  try {
    const { text, level = 'basic', model = 'gpt-4o-mini', mode } = JSON.parse(event.body)

    if (!text) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Text is required' })
      }
    }

    // Determine the analysis mode
    const analysisMode = mode || level

    // Define analysis structure based on mode
    const analysisStructure = {
      basic: [
        'Plain-Language Paraphrase',
        'Synopsis',
        'Key Words & Glosses',
        'Pointers for Further Reading'
      ],
      expert: [
        'Plain-Language Paraphrase',
        'Synopsis',
        'Language and Imagery',
        'Literary and Thematic Analysis',
        'Pointers for Further Reading'
      ],
      fullfathomfive: [
        'Textual Variants',
        'Plain-Language Paraphrase',
        'Language and Rhetoric',
        'Synopsis',
        'Key Words & Glosses',
        'Historical Context',
        'Sources',
        'Literary Analysis',
        'Critical Reception',
        'Similar phrases or themes in other plays',
        'Pointers for Further Reading',
        'New Variorum Analysis'
      ]
    }

    const structure = analysisStructure[analysisMode] || analysisStructure.basic

    // Check if text contains multiple lines
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const isMultipleLines = lines.length >= 2 && lines.length <= 5

    // Find relevant notes from Macbeth database (only for Full Fathom Five)
    let relevantNotes = []
    if (analysisMode === 'fullfathomfive') {
      try {
        relevantNotes = await findRelevantNotes(text)
        console.log('Macbeth notes loaded:', relevantNotes.length, 'notes found')
        console.log('Notes details:', relevantNotes)
      } catch (error) {
        console.error('Failed to load Macbeth notes, continuing without them:', error.message)
        relevantNotes = [] // Continue without notes if loading fails
      }
    }
    
    // Build the system prompt based on analysis mode
    let systemPrompt = ''
    const currentPlayName = 'Macbeth' // You can make this dynamic if needed
    const currentSceneName = 'ACT 1, SCENE 1' // You can make this dynamic if needed

    if (analysisMode === 'basic') {
      systemPrompt = `You are a university professor speaking to very smart undergraduates about Shakespeare.

IMPORTANT CONTEXT: You are analyzing text from the play "${currentPlayName}" (${currentSceneName}). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST provide responses for ALL of these sections in exactly this order:

**Plain-Language Paraphrase:**
**Synopsis:**
**Key Words & Glosses:**
**Pointers for Further Reading:**

FORMAT REQUIREMENTS:
- Use EXACTLY the section headers shown above - do not change them
- 2–4 sentences per section
- Complete sentences and paragraphs
- Clear, accessible language
- Always reference "${currentPlayName}" and "${currentSceneName}" directly
- Titles in <em>italics</em>, never in quotes or asterisks
- Key Words format: "word" means definition; "word" means definition (preserve capitalization)`
    } else if (analysisMode === 'expert') {
      systemPrompt = `You are a Shakespeare scholar writing for advanced students.

IMPORTANT CONTEXT: Analyze text from "${currentPlayName}" (${currentSceneName}).

FORMAT REQUIREMENTS:
- Structure your response into these sections in this exact order:

**Plain-Language Paraphrase:**
**Synopsis:**
**Language and Imagery:**
**Literary and Thematic Analysis:**
**Pointers for Further Reading:**

- Use essay-style paragraphs (no bullets/lists)
- Each section should be 5–8 sentences
- Clear but scholarly tone
- Titles in <em>italics</em>, never in quotes or asterisks
- Always reference "${currentPlayName}" and "${currentSceneName}"`
    } else if (analysisMode === 'fullfathomfive') {
      console.log('Full Fathom Five level detected - using comprehensive prompt with Textual Variants and Language and Rhetoric sections');
      console.log('DEBUG: Function version updated at', new Date().toISOString());
      systemPrompt = `You are an expert Shakespearean scholar providing the most comprehensive analysis possible.

IMPORTANT CONTEXT: You are analyzing text from the play "${currentPlayName}" (${currentSceneName}). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST provide responses for ALL of these sections in exactly this order. Do not skip any sections. EVERY section must be included:

**Textual Variants:** (REQUIRED - FIRST SECTION)  
**Plain-Language Paraphrase:** (REQUIRED)  
**Language and Rhetoric:** (REQUIRED - NEW SECTION)  
**Synopsis:** (REQUIRED)  
**Key Words & Glosses:** (REQUIRED)  
**Historical Context:** (REQUIRED)  
**Sources:** (REQUIRED)  
**Literary Analysis:** (REQUIRED)  
**Critical Reception:** (REQUIRED)  
**Similar phrases or themes in other plays:** (REQUIRED)  
**Pointers for Further Reading:** (REQUIRED)

FORMAT REQUIREMENTS:  
- Start each section with the exact heading format shown above (colons are already included).  
- Provide 6–12 sentences per section; use complete, scholarly style.  
- Use extensive critical citations from a broad range of critics.  
- Always italicize titles using \`<em>italics</em>\`, never quote them or italicize author names.  
- Use exact scholar names (e.g., A.C. Bradley), with full citation format.  
- **Key Words & Glosses**: Use format \`"word" means [definition]; "word" means [definition]\`.  
- **Textual Variants**: If none exist, say "Early editions are identical to Folger."  
- **Language and Rhetoric**: Include (1) etymology from 1914 OED, (2) rhetorical devices, (3) meter & rhythm, with citations.

CRITICAL CITATION REQUIREMENTS:  
- Include at least one critic per century (18th–21st), at least one Marxist critic, plus 2–3 random others.  
- Use full publication details.  
- Do not modify scholar names.

LENGTH: 800–1200 words total

**New Variorum Analysis:**
For this section, use the historical variorum notes provided below.  
- Display the EXACT notes linked to the line numbers passed in.  
- Do NOT summarize, truncate, or modify the notes in any way.  
- Do NOT invent or expand commentary beyond what is provided.  
- Show ALL notes from the database, not just summaries.
- DO NOT CUT OR TRUNCATE ANY NOTES - include the complete, full text.
- Even if notes are extremely long, you MUST include the ENTIRE text.
- Do not stop mid-sentence or cut off any part of the notes.
- Format each entry as:

[Line X] [EXACT commentary text from the provided notes]

- If no note exists for a line, output: [Line X] No commentary available.
- Notes must appear in the same order as the selected line numbers.
- Do not include notes for lines that are not explicitly selected.
- IMPORTANT: Copy the notes exactly as provided, word for word, without any changes.
- CRITICAL: Include the complete, unabridged text of every note, no matter how long.`
       
      // Add Macbeth notes if available
      if (relevantNotes.length > 0) {
        systemPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Here are the relevant notes found:`
        
        relevantNotes.forEach((note, index) => {
          systemPrompt += `\n\n[Line ${note.line}] ${note.play}`
          note.notes.forEach((noteText, noteIndex) => {
            systemPrompt += `\n\nNote ${noteIndex + 1}: ${noteText}`
          })
        })
        
        systemPrompt += `\n\nUse these exact notes in your "New Variorum Analysis" section. Format each note as: [Line X] [Commentary from notes]. Do not add any additional commentary or speculation.`
      }
    }



    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`

    if (isMultipleLines) {
      userPrompt += `\n\nThis selection contains ${lines.length} lines. Please provide analysis that considers both the individual lines and their relationship to each other.`
    }

    if (analysisMode === 'basic') {
      userPrompt += `\n\nPlease provide a Basic Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'expert') {
      userPrompt += `\n\nPlease provide an Expert Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide a Full Fathom Five analysis following the exact format specified in the system prompt.`
      
      if (relevantNotes.length > 0) {
        console.log('Adding notes to prompt. Total notes found:', relevantNotes.length)
        relevantNotes.forEach((note, index) => {
          console.log(`Note ${index + 1}: Line ${note.line}, ${note.notes.length} note entries`)
          note.notes.forEach((noteText, noteIndex) => {
            console.log(`  Note entry ${noteIndex + 1} length:`, noteText.length)
          })
        })
        
        userPrompt += `\n\nHISTORICAL VARIORUM NOTES TO USE:`
        relevantNotes.forEach((note, index) => {
          userPrompt += `\n\n[Line ${note.line}] ${note.play}`
          note.notes.forEach((noteText, noteIndex) => {
            // Include the complete, full text of every note
            userPrompt += `\n${noteText}`
          })
        })
        userPrompt += `\n\nCRITICAL INSTRUCTIONS: Use these EXACT notes in your "New Variorum Analysis" section. Copy them word for word without any changes, summaries, or modifications. Show ALL notes from the database, not just parts of them. DO NOT TRUNCATE OR CUT ANY NOTES. Include the complete, full text of every note. Even if the notes are very long, you MUST include the ENTIRE text. Do not stop mid-sentence or cut off any part. Format each note as: [Line X] [EXACT commentary text from notes]. Do not add any additional commentary or speculation.

ABSOLUTE REQUIREMENT: Every single character of the provided notes must appear in your response. NO EXCEPTIONS. You must copy the notes exactly as provided, word for word, character for character. FAILURE TO INCLUDE COMPLETE NOTES WILL RESULT IN INCOMPLETE ANALYSIS.

IMPORTANT: The notes above are the COMPLETE notes from the database. You MUST include ALL of them in your "New Variorum Analysis" section. Do not summarize, do not truncate, do not cut off. Copy them exactly as shown above.`
      }
    } else {
      userPrompt += `\n\nPlease provide a comprehensive ${analysisMode} analysis of this text.`
    }

    // Get max_tokens from request or use default
    const maxTokens = (analysisMode === 'fullfathomfive' ? 8000 : 3000)

    // Debug: Log the user prompt length
    console.log('User prompt length:', userPrompt.length)
    console.log('Max tokens:', maxTokens)
    
    // Use gpt-4o for full fathom five to handle longer responses better
    const modelToUse = analysisMode === 'fullfathomfive' ? 'gpt-4o' : model
    
    // Make the API call
    const completion = await openai.chat.completions.create({
      model: modelToUse,
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user",
          content: userPrompt
        }
      ],
      temperature: analysisMode === 'fullfathomfive' ? 0.3 : 0.7,
      max_tokens: maxTokens
    })
    
    // Debug: Log response length
    console.log('Response length:', completion.choices[0].message.content.length)
    console.log('Full response preview:', completion.choices[0].message.content.substring(0, 500))
    console.log('Response ends with:', completion.choices[0].message.content.substring(completion.choices[0].message.content.length - 200))

    const response = completion.choices[0].message.content

    // Parse the response into structured sections
    let analysis = {}
    
    // Parse structured analysis
    const sections = structure
    let currentSection = null
    let currentContent = []

    const responseLines = response.split('\n')
    
    for (const line of responseLines) {
      const trimmedLine = line.trim()
      
      // Check if this line starts a new section
      const matchingSection = sections.find(section => 
        trimmedLine.toLowerCase().includes(section.toLowerCase()) ||
        trimmedLine.toLowerCase().startsWith(section.toLowerCase().replace(/\s+/g, '').toLowerCase()) ||
        trimmedLine.toLowerCase().startsWith(section.toLowerCase().replace(/[^a-zA-Z]/g, '').toLowerCase())
      )

      if (matchingSection && !currentSection) {
        currentSection = matchingSection
        currentContent = []
      } else if (matchingSection && currentSection) {
        // Save previous section
        analysis[currentSection] = currentContent.join('\n').trim()
        currentSection = matchingSection
        currentContent = []
      } else if (currentSection && trimmedLine) {
        currentContent.push(trimmedLine)
      }
    }

    // Save the last section
    if (currentSection && currentContent.length > 0) {
      analysis[currentSection] = currentContent.join('\n').trim()
    }

    // Debug: Log what sections were found
    console.log('Parsed sections:', Object.keys(analysis))
    console.log('Looking for sections:', sections)
    
    // Check if New Variorum Analysis was captured
    if (analysis['New Variorum Analysis']) {
      console.log('New Variorum Analysis found, length:', analysis['New Variorum Analysis'].length)
    } else {
      console.log('New Variorum Analysis NOT found in parsed sections')
      // Try multiple patterns to find it manually in the response
      const patterns = [
        /\*\*New Variorum Analysis\*\*:?\s*([\s\S]*?)(?=\*\*|$)/i,
        /New Variorum Analysis:?\s*([\s\S]*?)(?=\*\*|$)/i,
        /New Variorum Analysis:?\s*([\s\S]*)/i
      ]
      
      for (const pattern of patterns) {
        const variorumMatch = response.match(pattern)
        if (variorumMatch) {
          console.log('Found New Variorum Analysis manually with pattern, length:', variorumMatch[1].length)
          analysis['New Variorum Analysis'] = variorumMatch[1].trim()
          break
        }
      }
      
      // If still not found, try to find it by looking for the notes content
      if (!analysis['New Variorum Analysis']) {
        const notesMatch = response.match(/(\[Line \d+\].*?)(?=\*\*|$)/s)
        if (notesMatch) {
          console.log('Found notes content manually, length:', notesMatch[1].length)
          analysis['New Variorum Analysis'] = notesMatch[1].trim()
        }
      }
    }

    // If parsing failed, return the raw response
    if (Object.keys(analysis).length === 0) {
      analysis = { 'Analysis': response }
    }

    // For Full Fathom Five, add the notes directly to the analysis object
    if (analysisMode === 'fullfathomfive' && relevantNotes.length > 0) {
      let notesContent = ''
      relevantNotes.forEach((note, index) => {
        notesContent += `[Line ${note.line}] ${note.play}\n`
        note.notes.forEach((noteText, noteIndex) => {
          notesContent += `${noteText}\n\n`
        })
      })
      analysis['New Variorum Analysis'] = notesContent.trim()
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        choices: [{
          message: {
            content: response
          }
        }],
        analysis: analysis,
        mode: analysisMode,
        text: text,
        lineCount: lines.length,
        relevantNotes: relevantNotes,
        usage: completion.usage
      })
    }

  } catch (error) {
    console.error('Error:', error)
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Internal server error',
        details: error.message 
      })
    }
  }
}
