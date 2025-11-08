# Setting Up MCP Servers for Event Discovery

This guide will help you set up MCP servers to enhance the sponsor discovery workflow.

## Option 1: Eventbrite MCP Server (Recommended)

### Installation

```bash
# Install the Eventbrite MCP server globally
npm install -g @mseep/eventbrite-mcp
```

### Configuration

Add to your Claude Desktop config file:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

**Configuration:**

```json
{
  "mcpServers": {
    "eventbrite": {
      "command": "npx",
      "args": ["-y", "@mseep/eventbrite-mcp"],
      "env": {
        "EVENTBRITE_API_TOKEN": "YOUR_EVENTBRITE_TOKEN_HERE"
      }
    }
  }
}
```

### Getting Your Eventbrite Token

1. Go to: https://www.eventbrite.com/account-settings/apps
2. Click your app: "Sponsor Discovery Tool"
3. Look for **"Personal OAuth Token"** or similar
4. Copy the token (should be 40-64 characters)
5. Add it to the config above

### Available Tools

Once set up, you'll have access to:
- `search_events` - Search for events with filters
- `get_event` - Get event details
- `get_venue` - Get venue information
- `list_categories` - Get all event categories

### Testing

After setting up, restart Claude Desktop and ask:
```
Search for technology conferences in San Francisco using Eventbrite
```

---

## Option 2: Meetup API Integration (Python)

Since there's no Meetup MCP server, we'll integrate Meetup API directly into the Python code.

### Get Meetup API Key

1. Go to: https://www.meetup.com/api/
2. Sign in and go to **API Keys** or **OAuth Consumers**
3. Create a new OAuth consumer or API key
4. Copy your API key

### Add to .env

```bash
MEETUP_API_KEY=your_meetup_api_key_here
```

### Update Python Code

We'll need to:
1. Create a `MeetupApiClient` class (similar to EventbriteApiClient)
2. Add Meetup search to `EventDiscoveryService`
3. Combine results from both Eventbrite and Meetup

---

## Hybrid Approach (Best Option)

**For Eventbrite:**
- Use MCP server (Claude can search directly)
- Keep Python fallback for when MCP isn't available

**For Meetup:**
- Add Python API client
- Integrate into discovery workflow

**Benefits:**
1. Claude can search events directly via MCP tools
2. Your Python app can search both Eventbrite and Meetup
3. More event sources = better sponsor discovery
4. Graceful fallback if APIs fail

---

## Next Steps

### Immediate (5 minutes):
1. Install Eventbrite MCP: `npm install -g @mseep/eventbrite-mcp`
2. Add to Claude Desktop config with your token
3. Restart Claude Desktop
4. Test: "Search Eventbrite for tech conferences"

### Short-term (30 minutes):
1. Get Meetup API key
2. Add to `.env`
3. I'll help you create a `MeetupApiClient` class
4. Integrate into discovery workflow

### Result:
- **3 data sources:** Eventbrite MCP + Eventbrite API + Meetup API
- **Better coverage:** More events = more sponsors
- **Redundancy:** If one fails, others still work

---

## Troubleshooting

### Eventbrite MCP not showing up
- Check Claude Desktop config file syntax (valid JSON)
- Restart Claude Desktop completely
- Check that `npx` is in your PATH
- Verify token is correct

### Meetup API issues
- Ensure API key is active
- Check rate limits
- Verify account permissions

### Python integration
- Ensure all dependencies installed: `pip install requests`
- Check `.env` file is loaded
- Look for error logs

---

## Support

- **Eventbrite MCP**: https://www.npmjs.com/package/@mseep/eventbrite-mcp
- **Eventbrite API**: https://www.eventbrite.com/platform/api
- **Meetup API**: https://www.meetup.com/api/
