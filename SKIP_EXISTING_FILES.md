# Skip Existing Files Feature

## ✅ Skip Existing Files Feature Complete!

Your `fetch_data.py` script now intelligently skips existing CSV files by default, with an optional `--overwrite` flag to force re-fetching.

## 🆕 New Features

### **⏩ Skip Existing Files (Default Behavior)**
- **Checks for existing CSV** before making API calls
- **Skips if file exists** - saves time and API calls
- **Clear skip message**: `⏩ Skipping {player_id}, file already exists`
- **Returns success** - counts as successful since data is available

### **🔄 Overwrite Flag**
- **`--overwrite` flag** to force re-fetching existing files
- **Useful for updates** - when you want fresh data
- **Explicit control** - you decide when to overwrite

### **📊 Enhanced Progress Display**
- **Shows overwrite status** in the header
- **Clear indication** of whether files will be skipped or overwritten
- **Consistent behavior** across all fetch modes

## 🔧 Usage Examples

### **Default Behavior (Skip Existing)**
```bash
# Skip existing files (default)
python3 fetch_data.py --popular
python3 fetch_data.py --all --max 100
python3 fetch_data.py --players 201939 2544
```

### **Force Overwrite**
```bash
# Overwrite existing files
python3 fetch_data.py --popular --overwrite
python3 fetch_data.py --all --overwrite
python3 fetch_data.py --players 201939 --overwrite
```

### **Mixed Scenarios**
```bash
# Fetch new players, skip existing ones
python3 fetch_data.py --all --max 200

# Update specific players
python3 fetch_data.py --players 201939 2544 --overwrite

# Update popular players
python3 fetch_data.py --popular --overwrite
```

## 📊 Output Examples

### **Skipping Existing Files:**
```
🚀 NBA Data Fetcher
============================================================
📅 Season: 2024-25
📁 Data directory: data
📦 Chunk size: 50
🔄 Max retries: 3
⏱️  Delay between requests: 1 second
📝 Overwrite existing files: No (skip existing)
============================================================

🎯 Fetching 2 specific players...

[1/2] Fetching player 1 of 2 (201939)
⏩ Skipping 201939, file already exists

[2/2] Fetching player 2 of 2 (1630173)
⏩ Skipping 1630173, file already exists

============================================================
📊 Final Results:
✅ Successful: 2
❌ Failed: 0
📈 Total: 2
```

### **Overwriting Existing Files:**
```
🚀 NBA Data Fetcher
============================================================
📅 Season: 2024-25
📁 Data directory: data
📦 Chunk size: 50
🔄 Max retries: 3
⏱️  Delay between requests: 1 second
📝 Overwrite existing files: Yes
============================================================

🎯 Fetching 1 specific players...

[1/1] Fetching player 1 of 1 (201939)
✅ Saved 70 games to data/201939_2024_25.csv

============================================================
📊 Final Results:
✅ Successful: 1
❌ Failed: 0
📈 Total: 1
```

## 🎯 Benefits

### **⏱️ Time Savings**
- **No unnecessary API calls** for existing files
- **Faster execution** when most files already exist
- **Respectful API usage** - only fetch what's needed

### **🔄 Incremental Updates**
- **Add new players** without re-fetching existing ones
- **Update specific players** with `--overwrite`
- **Flexible workflow** - choose what to update

### **🛡️ Reliability**
- **No data loss** - existing files are preserved
- **Consistent behavior** - same logic across all fetch modes
- **Clear feedback** - know exactly what's happening

## 🔍 Technical Details

### **File Existence Check**
- **Uses `os.path.exists()`** to check for CSV files
- **Checks normalized filename** - `{player_id}_{season}.csv`
- **Season normalization** - `2024-25` becomes `2024_25`

### **Return Value Logic**
- **Skip = Success** - returns `True` since data is available
- **Fetch = Success** - returns `True` if API call succeeds
- **Fetch = Failure** - returns `False` if API call fails

### **Function Updates**
- **`fetch_and_save()`** - added `overwrite` parameter
- **`fetch_all_players()`** - added `overwrite` parameter
- **`fetch_popular_players()`** - added `overwrite` parameter
- **All functions** pass `overwrite` parameter through

## 🚀 Recommended Workflows

### **Initial Data Collection:**
```bash
# Fetch all players (will skip existing, fetch new)
python3 fetch_data.py --all
```

### **Regular Updates:**
```bash
# Update popular players weekly
python3 fetch_data.py --popular --overwrite

# Add new players (skip existing)
python3 fetch_data.py --all --max 100
```

### **Selective Updates:**
```bash
# Update specific players
python3 fetch_data.py --players 201939 2544 --overwrite

# Add new players without overwriting
python3 fetch_data.py --all --max 200
```

## 🎉 Result

Your fetcher script now:
- ✅ **Skips existing files by default** - saves time and API calls
- ✅ **Supports overwrite flag** - when you need fresh data
- ✅ **Clear progress feedback** - know exactly what's happening
- ✅ **Consistent behavior** - works across all fetch modes
- ✅ **Efficient workflow** - perfect for incremental updates

The script is now even more efficient and user-friendly! 🏀
