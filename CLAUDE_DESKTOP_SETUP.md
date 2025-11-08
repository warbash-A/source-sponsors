# Claude Desktop MCP Configuration

## ✅ Eventbrite MCP Server Installed!

The Eventbrite MCP server has been installed globally with `npm install -g @mseep/eventbrite-mcp`.

## 📋 Next Steps: Add to Claude Desktop

You need to add the MCP server configuration to your Claude Desktop config file.

### Step 1: Find Your Claude Desktop Config File

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add the Configuration

Open the config file in a text editor and add the following:

**If the file is empty or doesn't exist, use this entire content:**

```json
{
  "mcpServers": {
    "eventbrite": {
      "command": "npx",
      "args": ["-y", "@mseep/eventbrite-mcp"],
      "env": {
        "EVENTBRITE_API_TOKEN": "QZ45E5B7PATD2NFQXTKHALHFD5C4KVVUJGSRKCRQNHWBWIYLOV"
      }
    }
  }
}
```

**If the file already has content, merge the "eventbrite" entry into your existing "mcpServers" object.**

For example, if you already have:
```json
{
  "mcpServers": {
    "some-other-server": {
      ...
    }
  }
}
```

Add the eventbrite entry like this:
```json
{
  "mcpServers": {
    "some-other-server": {
      ...
    },
    "eventbrite": {
      "command": "npx",
      "args": ["-y", "@mseep/eventbrite-mcp"],
      "env": {
        "EVENTBRITE_API_TOKEN": "QZ45E5B7PATD2NFQXTKHALHFD5C4KVVUJGSRKCRQNHWBWIYLOV"
      }
    }
  }
}
```

### Step 3: Restart Claude Desktop

**Important:** You must completely quit and restart Claude Desktop for the changes to take effect.

- **macOS**: Cmd+Q to quit, then reopen
- **Windows**: File → Exit, then reopen
- **Linux**: Quit completely, then reopen

### Step 4: Verify It's Working

After restarting Claude Desktop, start a new conversation and ask:

```
Can you search Eventbrite for technology conferences in San Francisco?
```

If the MCP server is working, I'll be able to search Eventbrite directly and show you real events!

## 🔍 Troubleshooting

### MCP Server Not Showing Up

1. **Check JSON Syntax**: Make sure your config file is valid JSON (no trailing commas, proper quotes)
2. **Check Token**: Verify the EVENTBRITE_API_TOKEN is correct
3. **Restart Completely**: Make sure you fully quit and restarted Claude Desktop
4. **Check Logs**: Look for MCP-related errors in Claude Desktop logs

### Finding Your Config File

If you can't find the config file:

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
```

**Windows:**
```cmd
explorer %APPDATA%\Claude
```

**Linux:**
```bash
xdg-open ~/.config/Claude/
```

If the directory or file doesn't exist, create it manually.

### Testing the MCP Package

You can test if the MCP package works standalone:

```bash
npx @mseep/eventbrite-mcp
```

This should start the MCP server and show connection info.

## 📝 Reference Files

- **Pre-configured JSON**: `claude_desktop_config.json` (in this directory)
- **Full Setup Guide**: `MCP_SETUP_GUIDE.md`

## 🎯 What You'll Get

Once configured, you'll be able to:
- ✅ Search Eventbrite events in real-time during conversations
- ✅ Get event details instantly
- ✅ Find venues and categories
- ✅ Discover potential sponsors through event analysis

## ⏭️ Next: Meetup Integration

The Meetup API integration is being added to the Python code (no MCP needed). This will give you:
- Events from both Eventbrite AND Meetup
- Better sponsor coverage
- More data sources for discovery

Check the Python code updates in the next commit!
