# Security Notice - API Keys Exposure Fix

## Issue
API keys and sensitive credentials were accidentally committed to Git history in the `.env` file.

## Actions Taken
1. ✅ Removed `.env` file from Git tracking
2. ✅ Replaced sensitive values with placeholders
3. ✅ Committed security fix

## Required Actions (URGENT)

### 1. Revoke Exposed API Keys Immediately

**Google Gemini API Key:**
- Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
- Delete the exposed key: `AIzaSyCBgjLQTWRqvA-fLsMjlfun7uWp3V_6QqI`
- Generate a new API key

**Zalo Bot Token:**
- Go to Zalo Developer Console
- Regenerate your bot token (current: `446149642099893122:...`)

**Supabase Keys:**
- Go to your Supabase Dashboard
- Rotate the exposed anon key
- Update RLS policies if needed

**SunWorld API Key:**
- Contact SunWorld support to revoke: `c239013191a5406392d1dd26cb082955`
- Request a new subscription key

### 2. Update Your Local .env File
Copy `.env.example` to `.env` and fill in your NEW API keys:
```bash
cp .env.example .env
```

### 3. Clean Git History (Optional but Recommended)
To completely remove sensitive data from Git history:
```bash
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all
git push origin --force --all
```

**Warning:** This rewrites Git history and will affect all collaborators.

### 4. Monitor for Unauthorized Usage
- Check your API usage dashboards for any suspicious activity
- Set up billing alerts and usage limits
- Review access logs

## Prevention
- ✅ `.env` is already in `.gitignore`
- ✅ `.env.example` provides template without sensitive data
- Consider using environment-specific config management
- Use pre-commit hooks to scan for secrets

## Date
October 24, 2025