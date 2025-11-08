# How to Get Your Eventbrite Private Token

You've successfully created your OAuth app! Now you need the **Private Token**.

## Steps to Get Private Token

### Option 1: From Your App Dashboard

1. **Go to**: https://www.eventbrite.com/account-settings/apps
2. **Click on** your app: "Sponsor Discovery Tool"
3. Look for a section called **"Your personal OAuth token"** or **"Private Token"**
4. You might see a button: **"Show Client Secret and OAuth Token"** or **"Show Token"**
5. Click it and copy the **OAuth Token** (not the Client Secret)

### Option 2: Generate a New Private Token

If you don't see the Private Token option:

1. On the same page: https://www.eventbrite.com/account-settings/apps
2. Look for **"Create Private Token"** or **"Generate Token"** button
3. Give it a name (e.g., "API Access")
4. Copy the generated token

## What to Look For

The Private Token should:
- Be **40-64 characters long**
- Look different from your Client Secret
- Be labeled as "OAuth Token" or "Private Token" or "Personal OAuth Token"

## Current Credentials Status

✓ **Application Key**: `VCUBJ6XZCART2UYN3D` (18 chars)
✓ **Client Secret**: `QZ45E5B7PATD2NFQXTKHALHFD5C4KVVUJGSRKCRQNHWBWIYLOV` (42 chars)
✗ **Private Token**: **MISSING - THIS IS WHAT YOU NEED!**

## Once You Have the Private Token

Update your `.env` file:

```bash
EVENTBRITE_API_KEY=<paste_your_private_token_here>
```

Then test:

```bash
python test_eventbrite.py
```

You should see:
```
✓ Success! Found XX categories
```

## Screenshot Hint

When you're on your app page, the layout typically looks like:

```
Application Key (Client ID): VCUBJ6XZCART2UYN3D
OAuth Client Secret: QZ45E5B7PAT... [Show]

Your personal OAuth token:
[Generate Token] or [Show Token]
```

Click that button to get your Private Token!
