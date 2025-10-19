# 📁 Study Folder Naming Demo

## ✅ **New Descriptive Folder Structure**

### **Before (Generic):**
```
local_uploads/
├── study_123/
├── study_456/
└── study_789/
```

### **After (Descriptive):**
```
local_uploads/
├── study_123_unilever_deodorant_research/
├── study_456_skincare_preference_study/
└── study_789_beverage_taste_test/
```

## 🔧 **How It Works**

### **Study Title Processing:**
1. **Original Title**: "Unilever Deodorant Research Study"
2. **Clean Special Characters**: Remove punctuation, keep letters/numbers/spaces
3. **Replace Spaces**: Convert spaces to underscores
4. **Lowercase**: Convert to lowercase
5. **Final Folder Name**: `study_123_unilever_deodorant_research_study`

### **Example Transformations:**

| Original Study Title | Folder Name |
|---------------------|-------------|
| "Unilever Deodorant Research" | `study_123_unilever_deodorant_research` |
| "Skincare Preference Study 2024" | `study_456_skincare_preference_study_2024` |
| "Beverage Taste Test - Q1" | `study_789_beverage_taste_test_q1` |
| "Global Consumer Insights" | `study_101_global_consumer_insights` |

## 📂 **Complete Folder Structure**

```
local_uploads/
├── study_123_unilever_deodorant_research/
│   ├── categories/
│   │   ├── deodorant_1.jpg
│   │   ├── deodorant_2.jpg
│   │   └── deodorant_3.jpg
│   ├── layers/
│   │   ├── layer_background.jpg
│   │   └── layer_overlay.png
│   ├── elements/
│   │   ├── element_1.jpg
│   │   └── element_2.jpg
│   └── backgrounds/
│       └── default_background.jpg
└── drafts/
    └── draft_456/
        ├── categories/
        └── layers/
```

## 🎯 **Benefits**

1. **Easy Identification**: Folder names clearly indicate study purpose
2. **Better Organization**: Multiple studies are easily distinguishable
3. **Professional Structure**: Clean, descriptive naming convention
4. **Backward Compatible**: Existing studies continue to work
5. **Developer Friendly**: Easy to locate specific study files

## 🚀 **Implementation**

The folder naming is automatically handled by the `StorageManager`:

```python
# When creating a study
study_title = "Unilever Deodorant Research"
study_id = "123"

# StorageManager automatically creates:
folder_name = "study_123_unilever_deodorant_research"
```

## 📝 **Technical Details**

- **Title Cleaning**: Removes special characters except letters, numbers, spaces, hyphens
- **Space Replacement**: Converts spaces and hyphens to underscores
- **Case Handling**: Converts to lowercase for consistency
- **Length Handling**: No truncation (maintains full descriptive name)
- **Conflict Resolution**: Overwrites existing files with same name (simplified approach)

The result is a clean, organized, and easily navigable file structure that makes study management much more intuitive! 🎉
