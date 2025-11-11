# JSON Agent Import Feature

## Overview

The Chrome extension now supports importing agents from JSON files. This allows you to manually create or export agent configurations and load them into the extension.

## JSON Schema

Agent JSON files must follow this exact schema:

```json
{
  "id": "unique_agent_id",
  "name": "Agent Name",
  "avatar_url": "https://example.com/avatar.png",
  "backstory": "Agent backstory describing personality and background",
  "personality_traits": [
    "trait1",
    "trait2",
    "trait3"
  ]
}
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the agent (e.g., "charizard_001") |
| `name` | string | Display name of the agent |
| `avatar_url` | string | URL or data URI for the agent's avatar image |
| `backstory` | string | Background story and personality description |
| `personality_traits` | array[string] | List of personality traits (minimum 1) |

### Validation Rules

- All fields are **required**
- All string fields must be **non-empty**
- `personality_traits` must be an **array** with at least **one string item**
- `id` must be **unique** (will prompt for overwrite if duplicate exists)

## How to Import

1. **Create JSON File**: Follow the schema above
2. **Open Extension**: Click the extension icon to open the side panel
3. **Click Import Button**: Click the 📂 (folder) button in the header
4. **Select File**: Choose your `.json` file
5. **Confirm**: The extension will validate and import the agent
6. **Success**: The extension automatically switches to the imported agent

## Example Agent

See `chrome_extension/example-agent.json` for a complete example:

```json
{
  "id": "charizard_001",
  "name": "Charizard",
  "avatar_url": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/6.png",
  "backstory": "I am Charizard, a powerful Fire/Flying-type Pokémon! I evolved from Charmeleon and love soaring through the skies with flames blazing from my tail. I'm fiercely loyal to my trainer and never back down from a challenge!",
  "personality_traits": [
    "brave",
    "competitive",
    "protective",
    "confident",
    "passionate"
  ]
}
```

## Avatar URLs

The `avatar_url` field accepts:

1. **HTTP/HTTPS URLs**: `https://example.com/image.png`
2. **Data URIs**: `data:image/png;base64,iVBORw0KG...`
3. **Relative paths**: `assets/icon128.png` (for bundled images)

### Converting Local Images to Data URIs

If you have a local image file, you can convert it to a data URI:

**Using Python:**
```python
import base64

with open('image.png', 'rb') as f:
    data = base64.b64encode(f.read()).decode()
    data_uri = f'data:image/png;base64,{data}'
    print(data_uri)
```

**Using Command Line (macOS/Linux):**
```bash
echo "data:image/png;base64,$(base64 -i image.png)" | pbcopy
```

**Using Online Tools:**
- https://www.base64-image.de/
- https://base64.guru/converter/encode/image

## Error Handling

The extension validates imported JSON and shows clear error messages:

### Missing Required Field
```
❌ Invalid JSON: Missing required field: "backstory"
```

### Invalid Type
```
❌ Invalid JSON: "personality_traits" must be an array
```

### Empty Array
```
❌ Invalid JSON: "personality_traits" must contain at least one trait
```

### Malformed JSON
```
❌ Invalid JSON file. Please check the file format.
```

### Duplicate Agent
If an agent with the same `id` already exists, you'll be prompted:
```
Agent "Charizard" (ID: charizard_001) already exists. Overwrite?
[Cancel] [OK]
```

## Tips

1. **Unique IDs**: Use descriptive IDs like `pokemon_name_number` (e.g., `pikachu_025`)
2. **Avatar Images**: For best results, use 128x128px PNG images
3. **Backstory**: Keep it concise but descriptive (2-3 sentences)
4. **Traits**: Choose 3-5 personality traits that define the agent
5. **Testing**: Import the example agent first to verify everything works

## Integration with AICraft

While you can manually create JSON files, the recommended workflow is:

1. Create agents in AICraft frontend
2. Click "Export to Extension" button (coming soon)
3. Agent automatically appears in extension via backend API

Manual JSON import is useful for:
- Testing custom agents
- Sharing agent configurations
- Backing up agent data
- Creating agents without AICraft frontend

## Troubleshooting

### Import Button Not Working
- Ensure you're running Chrome 88+ (Manifest V3 support)
- Check browser console for errors (F12 → Console)
- Reload the extension (chrome://extensions → Reload)

### Avatar Not Displaying
- Verify the URL is accessible
- Check if the image format is supported (PNG, JPG, GIF, WebP)
- Try using a data URI instead of an external URL

### Agent Not Appearing in Dropdown
- Check that the import showed success message
- Refresh the extension panel
- Check Chrome storage (F12 → Application → Storage → Local Storage)

### Validation Errors
- Use a JSON validator like https://jsonlint.com/
- Compare your JSON to the example file
- Ensure all required fields are present
- Check for typos in field names (case-sensitive)

## Storage Location

Imported agents are stored in Chrome's local storage:

- **Location**: `chrome.storage.local`
- **Key**: `agents` (object containing all agents)
- **Persistence**: Data persists across browser sessions
- **Limit**: ~10MB total storage (generous for agent data)

To view stored agents:
1. Open DevTools (F12)
2. Go to Application → Storage → Local Storage
3. Find the extension's origin
4. Look for the `agents` key

## Clearing Imported Agents

There's no bulk delete feature yet. To remove an agent:

1. **Manual Method**: Use DevTools to edit `chrome.storage.local`
2. **Clear All**: Clear extension data (chrome://extensions → Remove → Reinstall)
3. **Per-Agent History**: Use the 🗑️ (trash) button to clear chat history only

*Note: A "Remove Agent" feature may be added in the future.*
