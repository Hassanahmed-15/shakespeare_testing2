#!/usr/bin/env python3
"""
Script to generate loading functions for all new Shakespeare plays
"""

plays_data = [
    ("Julius Caesar", "julius_caesar", "julius_caesar.json"),
    ("King John", "king_john", "king_john.json"),
    ("Love's Labour's Lost", "loves_labours_lost", "loves_labours_lost.json"),
    ("The Merchant of Venice", "merchant_of_venice", "merchant_of_venice.json"),
    ("A Midsummer Night's Dream", "midsummer_nights_dream", "midsummer_nights_dream.json"),
    ("Much Ado About Nothing", "much_ado_about_nothing", "much_ado_about_nothing.json"),
    ("Richard II", "richard_ii", "richard_ii.json"),
    ("Richard III", "richard_iii", "richard_iii.json"),
    ("The Tempest", "the_tempest", "the_tempest.json"),
    ("The Winter's Tale", "the_winters_tale", "the_winters_tale.json"),
    ("Troilus and Cressida", "troilus_and_cressida", "troilus_and_cressida.json"),
    ("Twelfth Night", "twelfth_night", "twelfth_night.json")
]

# Generate loading functions
functions_code = ""
for display_name, var_name, filename in plays_data:
    function_code = f'''
            const load{var_name.replace('_', '').title()} = async () => {{
                try {{
                    console.log('🔄 Loading {display_name}...');
                    const response = await fetch('Public/Data/{filename}?v=' + Date.now());
                    
                    if (response.ok) {{
                        const {var_name}Data = await response.json();
                        window.{var_name}Data = {var_name}Data;
                        
                        plays['{var_name}'] = {{
                            name: '{display_name}',
                            originalFileName: '{var_name}',
                            characters: [],
                            acts: {{}},
                            scenes: {{}}
                        }};
                        
                        if ({var_name}Data) {{
                            let sceneCount = 0;
                            let lineCount = 0;
                            Object.keys({var_name}Data).forEach(originalSceneKey => {{
                                const sceneData = {var_name}Data[originalSceneKey];
                                if (sceneData && typeof sceneData === 'object') {{
                                    const sceneContent = [];
                                    Object.keys(sceneData).forEach(lineNum => {{
                                        const lineData = sceneData[lineNum];
                                        if (!lineData) return;
                                        const text = (typeof lineData === 'string') ? lineData : (lineData.play ?? lineData.text ?? lineData.line ?? null);
                                        if (text) {{
                                            sceneContent.push(text);
                                            lineCount++;
                                        }}
                                    }});
                                    if (sceneContent.length > 0) {{
                                        const optimizedContent = optimizeSpeakerNames(sceneContent);
                                        const normalizedKey = normalizeSceneKey(originalSceneKey);
                                        plays['{var_name}'].scenes[normalizedKey] = optimizedContent;
                                        sceneCount++;
                                        const actName = parseActFromScene(normalizedKey);
                                        if (actName) {{
                                            if (!plays['{var_name}'].acts[actName]) {{
                                                plays['{var_name}'].acts[actName] = [];
                                            }}
                                            if (!plays['{var_name}'].acts[actName].includes(normalizedKey)) {{
                                                plays['{var_name}'].acts[actName].push(normalizedKey);
                                            }}
                                        }}
                                    }}
                                }}
                            }});
                            console.log(`✅ {display_name} parsed: ${{sceneCount}} scenes, ${{lineCount}} lines`);
                        }}
                        return '{var_name}';
                    }} else {{
                        console.warn('❌ Could not load {display_name} data - Status:', response.status);
                        return null;
                    }}
                }} catch (error) {{
                    console.error('❌ Error loading {display_name}:', error);
                    return null;
                }}
            }};
'''
    functions_code += function_code

print("Generated loading functions:")
print(functions_code)

# Also generate the list for Promise.all()
promise_list = []
for display_name, var_name, filename in plays_data:
    function_name = f"load{var_name.replace('_', '').title()}"
    promise_list.append(f"                    {function_name}(),")

print("\n\nFor Promise.all():")
for item in promise_list:
    print(item)
