# Eventbrite API Setup Guide

## Current Issue

Your Eventbrite credentials are being rejected with **403 Access Denied** errors.

### Credential Status
- ✗ Private token: `TEY2GLOQZ4ASNC4YENB6` (20 chars - too short)
- ✗ API key: `PXCP2X6UTRYO757FWU` (18 chars - too short)
- ✗ Public token: `S2KD5XXUCSSVDNG3PAJ5` (20 chars - too short)

**Expected:** Valid Eventbrite OAuth tokens should be 40-64 characters long.

## How to Get Valid Eventbrite API Credentials

### Step 1: Create an Eventbrite Developer Account

1. **Sign up/Login to Eventbrite**: https://www.eventbrite.com
2. **Go to Account Settings**
3. **Navigate to Developer Links** or visit: https://www.eventbrite.com/account-settings/apps

### Step 2: Create an App or Get a Private Token

#### Option A: Create a Private OAuth Token (Recommended for Testing)

1. Click **"Create Private Token"** or **"Generate Token"**
2. Give it a name (e.g., "Sponsor Discovery App")
3. **Copy the full token** - it should look like:
   ```
   XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   (40-64 characters long)
   ```

#### Option B: Create an OAuth Application

1. Click **"Create New App"**
2. Fill in:
   - **Application Name**: "Sponsor Discovery"
   - **Application URL**: Your website or `http://localhost`
   - **OAuth Redirect URI**: `http://localhost/callback`
3. After creating the app, you'll get:
   - **App Key** (Client ID)
   - **Client Secret**
   - **Private Token** (use this one!)

### Step 3: Verify Your Token

Once you have the token, update your `.env` file:

```bash
EVENTBRITE_API_KEY=<your_full_private_token_here>
```

Then test it:

```bash
python test_eventbrite.py
```

You should see:
```
✓ Success! Found XX categories
```

## Troubleshooting

### If you still get 403 errors:

1. **Verify your account is approved**: Some Eventbrite developer accounts require approval
2. **Check API quotas**: Make sure you haven't exceeded rate limits
3. **Verify token permissions**: Ensure the token has read access
4. **Check account status**: Your Eventbrite account must be in good standing

### Alternative: Test with Public Events

If you can't get API access, the app will fall back to:
- Web scraping with Apify
- Sample event data for demonstration

## Support

- **Eventbrite API Docs**: https://www.eventbrite.com/platform/api
- **Eventbrite Developer Forum**: https://www.eventbrite.com/support/community
- **Contact Eventbrite Support**: support@eventbrite.com

## Expected Token Format

Valid Eventbrite OAuth tokens look like this:
```
ABCDEFGHIJ1234567890KLMNOPQRST1234567890XYZ
```

**Length:** 40-64 alphanumeric characters
**Format:** All caps letters and numbers

Your current tokens are too short and may be from a different system or incomplete setup.
