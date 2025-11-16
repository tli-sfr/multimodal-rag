# Chunk Display Improvements

## ✅ Enhanced "Uploaded Chunks" Display

### 🎯 Changes Made:

---

## 1. **Replace "Unknown" with Filename**

### ✅ Smart Status Label Logic

**Before:**
- If `upload_source` is missing → Status shows `[Unknown]`

**After:**
- If `upload_source` is missing:
  1. First, try to use `original_filename` → Status shows `[filename.ext]`
  2. If no `original_filename`, try to use `source` (extract filename from path) → Status shows `[filename.ext]`
  3. Only if both are missing → Status shows `[Unknown]`

**Example transformations:**

| Scenario | Before | After |
|----------|--------|-------|
| Has `upload_source='ui'` | `[Uploaded]` | `[Uploaded]` ✅ |
| Has `upload_source='script'` | `[Pre-loaded]` | `[Pre-loaded]` ✅ |
| No `upload_source`, has `original_filename='test.pdf'` | `[Unknown]` | `[test.pdf]` ✅ |
| No `upload_source`, has `source='/path/to/file.mp4'` | `[Unknown]` | `[file.mp4]` ✅ |
| No `upload_source`, no filename | `[Unknown]` | `[Unknown]` |

---

## 2. **Add "mock data" Tag**

### ✅ Automatic Mock Data Detection

**Logic:**
- Check if `tags` field contains `'mock_data'`
- If yes, append `(mock data)` to the end of the chunk title

**Before:**
```
Chunk 1 - 👤 Andrew Ng - 📄 andrew_ng_ai.txt [Pre-loaded]
```

**After (if mock data):**
```
Chunk 1 - 👤 Andrew Ng - 📄 andrew_ng_ai.txt [Pre-loaded] - (mock data)
```

**Implementation:**
```python
# Check if 'mock_data' is in tags
if 'mock_data' in tags or (isinstance(tags, list) and 'mock_data' in tags):
    title_parts.append("(mock data)")
```

---

## 📊 Complete Display Logic

### **Chunk Title Format:**

```
Chunk {i} - 👤 {speaker_name} - 📄 {filename} [{status}] - (mock data)
```

**Components:**
1. **Chunk number:** Always shown
2. **Speaker name:** Shown if `speaker_name` exists (with 👤 icon)
3. **Filename:** Shows `original_filename` if available, otherwise shows `modality`
4. **Status:** 
   - `[Uploaded]` if `upload_source='ui'`
   - `[Pre-loaded]` if `upload_source='script'`
   - `[{original_filename}]` if no upload_source but has original_filename
   - `[{filename from source}]` if no upload_source but has source path
   - `[Unknown]` if none of the above
5. **Mock data tag:** Shown if `'mock_data'` in `tags`

---

## 🎯 Examples:

### **Example 1: UI Upload**
```
Chunk 1 - 👤 Elon Musk - 📄 elon_musk_ai_danger.mp4 [Uploaded]
```

### **Example 2: Script Pre-loaded**
```
Chunk 2 - 👤 Andrew Ng - 📄 andrew_ng_lecture.txt [Pre-loaded]
```

### **Example 3: Mock Data**
```
Chunk 3 - 👤 Fei-Fei Li - 📄 fei_fei_li_cv.txt [Pre-loaded] - (mock data)
```

### **Example 4: Legacy Data with Original Filename**
```
Chunk 4 - 📄 research_paper.pdf [research_paper.pdf]
```

### **Example 5: Legacy Data with Source Path**
```
Chunk 5 - 📄 VIDEO [video_lecture.mp4]
```
(Extracted from `source='/path/to/video_lecture.mp4'`)

### **Example 6: Truly Unknown**
```
Chunk 6 - 📄 TEXT [Unknown]
```
(No upload_source, no original_filename, no source)

---

## 🧪 Testing:

**Streamlit is running at:** http://localhost:8501

**To verify changes:**

1. **Go to "Browse Data" tab**
2. **Check "Uploaded Chunks" section**
3. **Verify:**
   - [ ] Chunks with `upload_source='ui'` show `[Uploaded]`
   - [ ] Chunks with `upload_source='script'` show `[Pre-loaded]`
   - [ ] Chunks without `upload_source` but with `original_filename` show `[filename]`
   - [ ] Chunks without `upload_source` but with `source` show `[filename from path]`
   - [ ] Chunks with `'mock_data'` in tags show `(mock data)` at the end
   - [ ] Only truly unknown chunks show `[Unknown]`

---

## 📝 Code Changes:

**File modified:** `src/ui/app.py`

**Key changes:**

```python
# Get additional metadata
source = point.payload.get('source', None)
tags = point.payload.get('tags', [])

# Smart status label logic
if upload_source == 'ui':
    status_label = "Uploaded"
elif upload_source == 'script':
    status_label = "Pre-loaded"
else:
    # Try to use original_filename or source
    if original_filename:
        status_label = original_filename
    elif source:
        # Extract just the filename from the full path
        status_label = Path(source).name
    else:
        status_label = "Unknown"

# Add mock data tag if present
if 'mock_data' in tags or (isinstance(tags, list) and 'mock_data' in tags):
    title_parts.append("(mock data)")
```

---

## 🎉 Summary:

**Two improvements implemented:**

1. ✅ **Smarter status labels** - Use filename instead of "Unknown" when possible
2. ✅ **Mock data tagging** - Automatically show "(mock data)" tag for test data

**Benefits:**
- ✅ More informative chunk display
- ✅ Easy to identify mock/test data
- ✅ Better user experience when browsing chunks
- ✅ Clearer data provenance

**The Browse Data tab now provides much better visibility into where each chunk came from!**

🌐 **Refresh http://localhost:8501 to see the improvements!**

