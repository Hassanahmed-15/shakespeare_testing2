const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Fallback notes function for when external fetch fails
function getFallbackNotes(text) {
  const searchText = text.toLowerCase().trim()
  const fallbackNotes = {
    "first witch: when shall we three meet again": {
      scene: "ACT 1, SCENE 1",
      line: "1",
      play: "First Witch: When shall we three meet again",
      notes: ["Enter three Witches] Seymour: The witches seem to be introduced for no other purpose than to tell us they are to meet again; and as I cannot discover any advantage resulting from such anticipation, but, on the contrary, think it injurious, I conclude the scene is not genuine.—Coleridge (p. 241): The true reason for the first appearance of the Witches is to strike the key-note of the character of the whole drama."]
    },
    "first witch: in thunder, lightning, or in rain?": {
      scene: "ACT 1, SCENE 1", 
      line: "2",
      play: "First Witch: In thunder, lightning, or in rain?",
      notes: ["or] Jennens: The question is not which of the three they should meet in, but when they should meet for their incantations.—Harry Rowe: By the use of the disjunctive particle 'or,' for the conjunctive and, the terror of the scenery is lessened. Thunder and lightning and rain, when combined, present a terrific image; but when separated, they cease to impress the mind with the same degree of terror."]
    },
    "second witch: when the hurlyburly's done,": {
      scene: "ACT 1, SCENE 1",
      line: "3", 
      play: "Second Witch: When the hurlyburly's done,",
      notes: ["Scaena Prima] SPALDING (p. 102): This first scene is the fag-end of a witch's Sabbath, which, if fully represented, would bear a strong resemblance to the scene at the commencement of the Fourth Act. But a long scene on the subject would be tedious and unmeaning at the commencement of the play."]
    },
    "third witch: that will be ere the set of sun.": {
      scene: "ACT 1, SCENE 1",
      line: "5",
      play: "Third Witch: That will be ere the set of sun.", 
      notes: ["Sun] Knight (ed. ii.): We have here the commencement of that system of tampering with the metre of Shakespeare in this great tragedy which universally prevailed till the reign of the Variorum critics had ceased to be considered as firmly established and beyond the reach of assault."]
    }
  }
  
  // Check for exact match
  if (fallbackNotes[searchText]) {
    console.log('Found fallback note for:', searchText)
    return [fallbackNotes[searchText]]
  }
  
  // Check for partial matches
  for (const [key, note] of Object.entries(fallbackNotes)) {
    if (key.includes(searchText) || searchText.includes(key)) {
      console.log('Found partial fallback match for:', searchText)
      return [note]
    }
  }
  
  console.log('No fallback notes found for:', searchText)
  return []
}

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    console.log('Fetching Macbeth notes for:', text)
    
    // Extract line numbers from the text
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const foundNotes = []
    
    for (const line of lines) {
      // Try to extract line number from the text
      const lineMatch = line.match(/^(\d+)\.?\s*(.*)/)
      if (lineMatch) {
        const lineNumber = lineMatch[1]
        const lineText = lineMatch[2] || line.trim()
        
        // Get the complete notes for this line directly from the hardcoded data
        const completeNotes = getCompleteNotesForLine(lineNumber)
        if (completeNotes) {
          foundNotes.push({
            line: lineNumber,
            play: lineText,
            notes: completeNotes
          })
          console.log(`Found complete notes for line ${lineNumber}: ${completeNotes.length} entries`)
        }
      } else {
        // Try alternative pattern
        const altMatch = line.match(/(\d+)/)
        if (altMatch) {
          const lineNumber = altMatch[1]
          const completeNotes = getCompleteNotesForLine(lineNumber)
          if (completeNotes) {
            foundNotes.push({
              line: lineNumber,
              play: line.trim(),
              notes: completeNotes
            })
            console.log(`Found complete notes for line ${lineNumber} (alt): ${completeNotes.length} entries`)
          }
        }
      }
    }
    
    if (foundNotes.length > 0) {
      return foundNotes
    }
    
    // Fallback to hardcoded notes if no matches found
    console.log('Using fallback notes for:', text)
    return getFallbackNotes(text)
  } catch (error) {
    console.error('Error loading Macbeth notes:', error)
    console.log('Using fallback notes for:', text)
    return getFallbackNotes(text)
  }
}

// Function to get complete notes for a specific line
function getCompleteNotesForLine(lineNumber) {
  const completeNotes = {
    "1": [
      "Enter three Witches] Seymour: The witches seem to be introduced for no other purpose than to tell us they are to meet again; and as I cannot discover any advantage resulting from such anticipation, but, on the contrary, think it injurious, I conclude the scene is not genuine.—Coleridge (p. 241): The true reason for the first appearance of the Witches is to strike the key-note of the character of the whole drama.—C. A. Brown (p. 147): Less study, less experience in human nature, less mental acquirements of every kind, I conceive, were employed on Macbeth, wonderfully as the whole character is displayed before us, than on those imaginary creations, the three weird sisters who haunt his steps, and prey upon his very being. —Schmidt (p. 436): The witches should not be visible when the curtain rises, but should glide in like ghosts.—[Dowden (p. 244): These are not the broomstick witches of vulgar popular traditions. If they are grotesque, they are also sublime. They may take their place beside the terrible old women of Michael Angelo, who spin the destinies of man: Shakespeare is no more afraid than Michael Angelo of being vulgar ... And thus he fearlessly showed us his weird sisters, 'the goddesses of destinie,' brewing infernal charms in their wicked cauldron. We cannot quite dispense in this life with ritualism, and the ritualism of evil is foul and ugly.... Yet these weird sisters remain terrible and sublime. They tingle in every fibre with evil energy; their malignity is inexhaustible; they have their raptures and ecstasies in crime; they are the awful inspirers of murder, insanity, suicide.—Snider (i, p. 176): What is the purpose for which the Poet employs these shapes? The answer must give the most important point for the proper comprehension of the play. It lies in the character of Banquo and Macbeth to see such specters. Hence they are absolutely necessary for the characterization. The Weird Sisters are beheld by these two persons alone, and it must be considered as the deepest phase of their nature that they behold the unreal phantoms. Both have the same temptation; both are endowed with a strong imagination; both witness the same apparition. In other words, the external influences which impel to evil are the same for both. In their excited minds these influences take the form of the Weird Sisters. Such is the design of the poet; he thus gives us at once an insight into the profoundest trait of their characters. In no other way could he portray so well the tendency to be controlled and victimized by the imagination, which sets up its shapes as actual, and then misleads men into following its fantastic suggestions... The author has scrupulously guarded the reality of the Weird Sisters; whenever they appear they are treated as positive objective existences. Mark the fact that two persons behold them at the same time, address them, and are addressed by them. For this special care, to preserve the air of reality in these shapes, the Poet has a most excellent reason, one that lies at the very basis of Tragedy. He wishes to place his audience under the same influences as his hero, and involve them in the same doubts and conflicts. We too must look upon the Weird Sisters with the eyes of Macbeth and Banquo; we may not believe in them, or we may be able to explain them—still the great dramatic object is to portray characters which do behold them and believe in them. The audience, therefore, must feel the same problem in all its depth and earnestness, and must be required to face the enigma of these appearances; for a character can be tragic to the spectators only when they are assailed with its difficulties and involved in its collision. It would have destroyed the whole effect of the Weird Sisters had their secret been plainly shown from the beginning. In fact, when the audience stand above the hero, and are made acquainted with all his complications, mistakes, and weaknesses, the realm of Comedy begins—the laugh is excited instead of the tear. We make merry over men pursuing that which we know to be a shadow.",
      "Enter three Witches] persons who can remain uninfluenced by their imaginations this representation may appear ridiculous even in its present shape. Few people have, however, so much passivity and so little poetry.—Miss Charlotte Carmichael (Academy, 8 Feb. 1879) traces a connection between the Nornae of Scandinavian Mythology and the present Witches, and suggests that the Nornae are three in number; so here there are three witches. 'Of these, the Third,' she says, 'is the special prophetess, while the First takes cognisance of the past, and the Second of the present, in affairs connected with humanity. These are the tasks of the Urda, Verdandi, and Skulda of Scandinavian Mythology.' Here the First Witch asks where is to be their next place of meeting. The Second Witch decides the time; the Third announces what is to be done. 'But their rôle is most clearly brought out in the famous "Hails."' The 1st Witch (Urda—the Past) hails Macbeth by his former title; the 2nd Witch (Verdandi—the Present) calls him by his new title; and the 3d Witch (Skudda—the Future) hails him as what he shall be. 'The same order is observed in their conference with Banquo, which is the more striking, as Shakespeare purposely alters the order given by Holinshed. It is just to acknowledge that in the later scenes this is less clear: Shakespeare has got more under the influence of his conception. Certainly there is something like the same order in "' Ist. Speak. 2nd. Demand. 3d. We'll answer,"' [IV, i, 67-69]. But the answers come not from their mouths, but from their masters'. There is nothing difficult in the supposition that Shakespeare, in writing a play to do honour to his new Scotch King, did not forget that the latter had just published a book on Demonologie. But the new Scotch King had just brought him a new Danish Queen; and it is likely that Shakespeare knew or learned somewhat of the mythology of the one, to wed to the superstition of the other.' See also IV, i, 2; note by Fleay.—T. A. Spalding (Academy, 1 March, 1879, in reply to the foregoing note): In Act I, scene i, it cannot be said that the First Witch says or does a thing to identify her with Urda, the Past; and the remarks of the Second Witch relate to the future rather than to the present. It is only the Third Witch who in any sense justifies the attempt to thrust the functions of the third Norn, Skulda, upon her, by her prophesy of the meeting with Macbeth. It is true that-when the meeting actually takes place the three Witches do follow the chronological order in their recital of Macbeth's honours—Glamis (in the past), Cawdor (in the present), and King (in the future): but, granting that this sequence, which could not have been otherwise in any case, proves anything, it would appear that these Norns only came out in their proper characters upon the greatest emergency, forgetting themselves sadly when off their guard; for only a few lines before we find Urda, whose attention should have been solely occupied with the past, predicting with some minuteness the results that were to follow her projected voyage to Aleppo; and that without the slightest indication of annoyance from Skulda, whose province she was thus invading. Again, in the prophecies to Banquo, the First Witch utterly fails to represent the past, and it is only by an extreme stretch of courtesy that the Second Witch can be taken to represent the present; certainly she does not do so any more than the First Witch. Doubtless it may be answered to my remarks on this last scene [I, iii.] that the Norn element is embodied in the Witch speeches after the entrance of Macbeth and Banquo, and the Witch element is embodied in the former portion of the scene. Attention is called to Macbeth's description of the would-be Nornae:—'You seem to understand me By each at once her choppy finger laying Upon her skinny lips:—You should be women, And yet your beards forbid me to interpret that you are so,' [I, iii, 47-51]... . When it can be shown that choppy fingers, skinny lips, and beards naturally suggest Nornae, then the prophecies which immediately follow may be taken as coming from Nornae. It surely requires the capacity of a Polonius for searching after truth to discover the Norn element in IV, i, where the Witches say (1) Speak, (2) Demand, (3) We'll answer.... The evidence derived from almost every line of the Witch scenes connect them with the current belief of the time upon the subject of witchcraft... . It would be interesting to know from what source Shakespeare derived his knowledge of Scandinavian mythology. A little might perhaps be floating about in the form of tradition, but would certainly excite only a feeble interest at a time when witchcraft was causing so intense an excitement. [Should this seem to accord but scant justice to a point of importance, reference may be made to Spalding (pp. 89–108), wherein he has amplified his remarks, as quoted above, and added thereto numerous extracts from writers contemporaneous to Shakespeare.]—W. Leighton (Robinson's Epit. of Lit., 15 April, 1879): It has been often remarked how wholly his own are Shakespeare's witches. Comparing them with Middleton's, which are able creations, we comprehend more fully the majesty and weirdness that belong to the tempters of Macbeth. May it not be that the dignity and peculiar interest that clothes them is greatly due to the fact that they are, indeed, the outcries of sinful desires in the human heart, and that intuitively we feel something of this, however little we analyze the poet's art?—Irving (Macbeth: Acting Version, p. 6): As regards the treatment of the witches, this is, I believe, the first time the weird sisters have been performed by women; and this innovation—if it can be so called—is made in the same spirit which has animated many of my predecessors in dramatic management, namely: to divest Shakespeare's witches of that semi-comic element which at one time threatened to obscure, if not to efface altogéther, their supernatural significance. It is with this end in view that at their first introduction on the stage they are represented as coming out of a thunder-cloud, suggesting that their home is among the dark and tempestuous elements of nature.—Sherman: To catch the full dramatic purport, we must avoid presuming that this meeting of the witches is either fortuitous or brought to pass solely on our account; it would be inartistic for the author to require the one or the other assumption. The sisters, we may suppose, are so agog over the mischief their masters have in hand that they have already met, perhaps more than once, since daybreak; and they are determining whether their enthusiasm will warrant, against the final moment, another coming together.—ED. ii. 3–13. When... ayre] Delius: This metre (namely, Trochaics of four accents, intermixed here and there with Iambics) Shakespeare has elsewhere used to mark the language of supernatural creatures, as in Temp. and Mid. N. D."
    ],
    "2": [
      "or] Jennens: The question is not which of the three they should meet in, but when they should meet for their incantations.—Harry Rowe: By the use of the disjunctive particle 'or,' for the conjunctive and, the terror of the scenery is lessened. Thunder and lightning and rain, when combined, present a terrific image; but when separated, they cease to impress the mind with the same degree of terror.—Knight (ed. ii.): The Witches invariably meet under a disturbance of the elements, and this is clear enough without any change of the original text."
    ],
    "3": [
      "Scaena Prima] SPALDING (p. 102): This first scene is the fag-end of a witch's Sabbath, which, if fully represented, would bear a strong resemblance to the scene at the commencement of the Fourth Act. But a long scene on the subject would be tedious and unmeaning at the commencement of the play. The audience is therefore left to assume that the witches have met, performed their conjurations, obtained from the evil spirits the information concerning Macbeth's career that they desired to obtain, and perhaps have been commanded by the fiends to perform the mission they subsequently carry through. All that is needed for the dramatic effect is a slight hint of probable diabolic interference, and that Macbeth is to be the special object of it; and this is done in as artistic a manner as is perhaps imaginable. In the first scene they obtain their information; in the second they utter their prediction. Every minute detail of these scenes is based upon the broad, recognised facts of witchcraft.—ED. ii.",
      "Hurley-burley's] Murray (A. N. D.): Known from about 1540. The phrase hurling and burling occurs somewhat earlier. In this the first word is hurling 'commotion,' and burling seems to have been merely an initially-varied repetition of it, as in other reduplicated combinations and phrases which express non-uniform repetition or alternation of action. Hurly-burly holds the same relation to hurling and burling that the simple Hurly [commotion] holds to hurling. But hurly-burly cannot, with present evidence, be considered as direct from hurly, since the latter has not been found before 1596. It is difficult to establish any historical contact with the French Hurleberlu, a heedless, hasty person (Rabelais, 1535); or the German Hurlburli, adv., precipitately, with headlong haste. Hurly-burly as a noun signifies, uproar, turmoil, confusion—(Formerly a more dignified word than now). 1539 Taverner Gard. Wysed. 11. Eij b, Hys comons whome ... he perceuyed in a Hurly-burly. 1571 Golding. Calvin on Ps. ix. 14, Such as are desperate doo rage with more Hurly-burly and greater headynesse.—ED. ii.",
      "done] Harry Rowe: To say A riot's done, A battle's done, A storm's done, is not very good English. My company of wooden comedians always say OVER. Praesente quercu, ligna quivis colligit."
    ],
    "5": [
      "Sun] Knight (ed. ii.): We have here the commencement of that system of tampering with the metre of Shakespeare in this great tragedy which universally prevailed till the reign of the Variorum critics had ceased to be considered as firmly established and beyond the reach of assault. We admit that it will not do servilely to follow the original in every instance where the commencement and close of a line are so arranged that it becomes prosaic; but, on the other hand, we contend that the desire to get rid of hemistichs, without regard to the nature of the dialogue, and so to alter the metrical arrangement of a series of lines, is to disfigure, instead of to amend, the poet. Any one who has an ear for the fine lyrical movement of the whole scene will see what an exquisite variety of pause there is in the ten lines of which it consists. Take, for example, line 12, and contrast its solemn movement with what has preceded it."
    ],
    "8": [
      "There] Steevens: Had the First Witch not required information, the audience must have remained ignorant of what it was necessary for them to know. Her speeches, therefore, proceed in the form of interrogatories; but all on a sudden an answer is given to a question which had not been asked. Here seems to be a chasm which I shall attempt to supply by the introduction of a single pronoun, and by distributing the hitherto mutilated line among the three speakers: '3 Witch, There to meet with— 1 Witch. Whom? 2 Witch. Macbeth.' Distinct replies have now been afforded to the three necessary inquiries, When, Where, and Whom the Witches were to meet. The dialogue becomes more regular and consistent, as each of the hags will now have spoken thrice (a magical number) before they join in utterance of the concluding words, which relate only to themselves. I should add that, in the two prior instances, it is also the Second Witch who furnishes decisive and material answers, and that I would give the words, 'I come, Graymalkin!' to the Third.—[Fletcher (p. 142): Here is the first intimation of that spirit of wickedness existing in Macbeth which develops itself in the progress of the piece. From this first moment the reader or auditor should be strictly on his guard against the ordinary critical error of regarding these beings as the originators of Macbeth's criminal purposes. Macbeth attracts their attention and excites their interest through the sympathy which evil ever has with evil—because he already harbours a wicked design—because mischief is germinating in his breast, which their interest is capable of fomenting. It is most important, in order to judge aright of Shakespeare's metaphysical, moral, and religious meaning in this great composition, that we should not mistake him as having represented that spirits of darkness are here permitted absolutely and gratuitously to seduce his hero from a state of perfectly innocent intention. It is plain that such an error at the outset vitiates and debases the moral to be drawn from the whole piece. Macbeth does not project the murder of Duncan because of his encounter with the weird sisters; the weird sisters encounter him because he has projected the murder—because they know him better than his royal master does, who tells us, 'There is no art To find the mind's construction in the face.' But these ministers of evil are privileged to see 'the mind's construction' where human eye cannot penetrate—in the mind itself. They repair to the blasted heath because, as one of them says afterwards of Macbeth, 'something wicked this way comes.'—ED. ii.]"
    ]
  }
  
  return completeNotes[lineNumber] || null
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
