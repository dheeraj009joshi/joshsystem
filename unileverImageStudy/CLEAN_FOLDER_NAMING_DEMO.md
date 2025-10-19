# 📁 Clean Study Folder Naming

## ✅ **Simplified Folder Structure**

### **Before (With Study ID):**
```
local_uploads/
├── study_123_unilever_deodorant_research/
├── study_456_skincare_preference_study/
└── study_789_beverage_taste_test/
```

### **After (Clean Study Title Only):**
```
local_uploads/
├── study_unilever_deodorant_research/
├── study_skincare_preference_study/
└── study_beverage_taste_test/
```

## 🔧 **How It Works**

### **Study Title Processing:**
1. **Original Title**: "Unilever Deodorant Research Study"
2. **Clean Special Characters**: Remove punctuation, keep letters/numbers/spaces
3. **Replace Spaces**: Convert spaces to underscores
4. **Lowercase**: Convert to lowercase
5. **Final Folder Name**: `study_unilever_deodorant_research_study`

### **Example Transformations:**

| Original Study Title | Folder Name |
|---------------------|-------------|
| "Unilever Deodorant Research" | `study_unilever_deodorant_research` |
| "Skincare Preference Study 2024" | `study_skincare_preference_study_2024` |
| "Beverage Taste Test - Q1" | `study_beverage_taste_test_q1` |
| "Global Consumer Insights" | `study_global_consumer_insights` |

## 📂 **Complete Folder Structure**

```
local_uploads/
├── study_unilever_deodorant_research/
│   ├── grid_categories/
│   │   ├── brands/
│   │   │   ├── dove.jpg
│   │   │   ├── axe.jpg
│   │   │   └── rexona.jpg
│   │   ├── fragrances/
│   │   │   ├── ocean_breeze.jpg
│   │   │   └── fresh_citrus.jpg
│   │   └── formats/
│   │       ├── spray.jpg
│   │       └── roll_on.jpg
│   ├── layers/
│   │   ├── background.jpg
│   │   └── overlay.png
│   └── elements/
│       └── element_1.jpg
├── study_skincare_preference_study/
│   ├── grid_categories/
│   │   ├── product_types/
│   │   └── skin_concerns/
│   └── layers/
└── drafts/
    └── draft_456/
        ├── grid_categories/
        └── layers/
```

## 🎯 **Benefits**

1. **Cleaner Names**: No random IDs cluttering folder names
2. **More Readable**: Easy to identify studies by title
3. **Professional Look**: Clean, descriptive naming
4. **Better Organization**: Intuitive folder structure
5. **Simplified URLs**: Shorter, cleaner file paths

## 🚀 **URL Structure**

### **Before:**
```
/static/uploads/study_123_unilever_deodorant_research/grid_categories/brands/dove.jpg
```

### **After:**
```
/static/uploads/study_unilever_deodorant_research/grid_categories/brands/dove.jpg
```

## 📝 **Technical Implementation**

### **Folder Name Generation:**
```python
# Clean the title for folder name
clean_title = re.sub(r'[^\w\s-]', '', study_title)  # Remove special chars
clean_title = re.sub(r'[-\s]+', '_', clean_title)  # Replace spaces with underscores
clean_title = clean_title.strip('_').lower()  # Lowercase and clean
folder_name = f"study_{clean_title}"  # Clean naming without ID
```

### **Example Usage:**
```python
# Study title: "Unilever Deodorant Research"
# Result: "study_unilever_deodorant_research"

# Study title: "Skincare Study 2024"
# Result: "study_skincare_study_2024"
```

## 🎊 **Result**

Study folders now have clean, descriptive names based solely on the study title, making them much more readable and professional! 🎉

### **Key Changes:**
- ❌ `study_123_unilever_deodorant_research` (with random ID)
- ✅ `study_unilever_deodorant_research` (clean title only)

The folder structure is now much cleaner and more intuitive to navigate!
