# GitHub Traffic Data Fetch Instructions

**Date:** November 1, 2025  
**Script Created:** `scripts/fetch_github_traffic.py`

---

## Current Status

✅ **Script Created:** `scripts/fetch_github_traffic.py`  
✅ **Script Tested:** Ran successfully (requires authentication token)  
⏸ **Data Fetch:** Requires GitHub Personal Access Token

---

## What the Script Does

The script fetches traffic statistics for both repositories:
- **PaiiD Main:** SCPrime/PaiiD
- **PaiiD-2mx:** SCPrime/Pa-D-2mx

**Data Retrieved:**
- Page views (last 14 days) - Total views and unique visitors
- Clone activity (last 14 days) - Total clones and unique cloners
- Top referring sites
- Most viewed files/paths

---

## How to Get the Data

### Step 1: Create GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "PaiiD Traffic Fetcher"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `public_repo` (if repositories are public)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

### Step 2: Run the Script with Token

**Option A: Using Command Line Argument**
```bash
cd C:\Users\SSaint-Cyr\Documents\GitHub\PaiiD
python scripts/fetch_github_traffic.py --token YOUR_TOKEN_HERE
```

**Option B: Using Environment Variable (More Secure)**
```powershell
# Set environment variable (current session only)
$env:GITHUB_TOKEN = "YOUR_TOKEN_HERE"
python scripts/fetch_github_traffic.py
```

**Option C: Permanent Environment Variable (Windows)**
1. Open System Properties → Environment Variables
2. Add new User variable:
   - Name: `GITHUB_TOKEN`
   - Value: `YOUR_TOKEN_HERE`
3. Restart terminal/PowerShell
4. Run: `python scripts/fetch_github_traffic.py`

### Step 3: View Results

The script generates two files:
- **`github_traffic_data.json`** - Raw JSON data (machine-readable)
- **`github_traffic_data.txt`** - Human-readable report

---

## Output Format

### JSON Output (`github_traffic_data.json`)
```json
{
  "generated": "2025-11-01T20:00:07Z",
  "repositories": [
    {
      "repository": "SCPrime/PaiiD",
      "timestamp": "...",
      "page_views": {
        "count": 123,
        "uniques": 45,
        "views": [...]
      },
      "clones": {
        "count": 12,
        "uniques": 8,
        "clones": [...]
      },
      ...
    }
  ]
}
```

### Text Report (`github_traffic_data.txt`)
```
======================================================================
GitHub Traffic Report: SCPrime/PaiiD
Generated: 2025-11-01T20:00:07Z
======================================================================

[PAGE VIEWS] Last 14 Days:
   Total Views: 123
   Unique Visitors: 45
   
   Daily Breakdown:
   2025-10-25: 15 views (8 unique)
   ...

[CLONE ACTIVITY] Last 14 Days:
   Total Clones: 12
   Unique Cloners: 8
   ...
```

---

## Important Notes

### Data Limitations
- **GitHub API only provides last 14 days** of traffic data
- **Historical data is NOT available** via API
- **File-level downloads** are NOT tracked (only clones)
- **Individual user identification** is NOT available (privacy)

### What Counts as "Download"
- **Clones:** When someone runs `git clone` or downloads ZIP
- **Page Views:** When someone views repository pages on GitHub
- **NOT tracked:** Individual file downloads, API calls, direct file access

### Access Requirements
- **Repository owner/admin** can view via GitHub web interface
- **API access** requires personal access token with `repo` scope
- **Public repositories:** Token still required for API access

---

## Alternative: Manual Check

If you prefer to check manually:

1. **PaiiD Main:**
   - Visit: https://github.com/SCPrime/PaiiD/insights/traffic
   - View: Page views, clones, referring sites

2. **PaiiD-2mx:**
   - Visit: https://github.com/SCPrime/Pa-D-2mx/insights/traffic
   - View: Page views, clones, referring sites

**Note:** GitHub web interface shows same 14-day window, but provides visual charts and easier navigation.

---

## Script Location

**File:** `scripts/fetch_github_traffic.py`

**Usage:**
```bash
# Basic usage (requires token)
python scripts/fetch_github_traffic.py --token YOUR_TOKEN

# Custom repositories
python scripts/fetch_github_traffic.py --token YOUR_TOKEN --repos owner/repo1 owner/repo2

# Custom output file
python scripts/fetch_github_traffic.py --token YOUR_TOKEN --output my_traffic.json
```

---

## Security Note

⚠️ **NEVER commit your GitHub token to the repository!**

- Token is stored in environment variable (recommended)
- Or passed via command line (less secure, visible in process list)
- Script will use `GITHUB_TOKEN` environment variable if set
- Token should have minimal required scopes (`repo` scope only)

---

**Script Status:** ✅ Ready to use (requires token)  
**Next Step:** Create GitHub token and run script to fetch actual data

