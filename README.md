# 🔐 Android Keystore Setup - Automated Configuration

An automated script to create Android Keystore and Code Signing in seconds, eliminating tedious manual steps.

## ✨ Features

- **Automatic Keystore Generation** - No complex manual steps required
- **Auto-Update build.gradle** - Automatically configures signing settings
- **Firebase Support** - Automatic backup and Git protection for Firebase files
- **Groovy & Kotlin DSL Support** - Works with both build.gradle formats
- **Smart JDK Detection** - Auto-finds Java installation on Windows, macOS, and Linux
- **Automatic Backups** - Creates backup copies of original configuration files

---

## 📋 Requirements

### ✅ Required

- **Java JDK 17 or newer** (installed on your system)
- **Python 3.7+** (to run the script)
- **Flutter Project** (prepared and ready)

### ✅ Optional

- **Firebase** (if you're using it in your project)

---

## 🚀 Quick Start

### Step 1: Prepare the Script

Copy `setup_keystore.py` to your project root:

```bash
cd your-flutter-project
# Place the script in the main project folder
```

### Step 2: (Optional) Customize Configuration

Edit the `CONFIG` section in the script with your company details:

```python
CONFIG = {
    "company_name": "Your Company Name",
    "developer_name": "Your Name",
    "organization": "Your Organization",
    "city": "Cairo",
    "state": "Cairo",
    "country": "EG",
    "password": "strong-password-here",  # ⚠️ Change this password!
}
```

### Step 3: Run the Script

```bash
python setup_keystore.py
```

### Step 4: Follow the Prompts

If you have an existing keystore, the script will ask if you want to replace it.

---

## 📁 Generated Files

After running the script, you'll find these files in the `necessary_files/` directory:

```
necessary_files/
├── upload-keystore.jks          # Main Keystore file
├── key.properties               # Signing credentials
├── firebase-info.txt            # Firebase information (if present)
├── google-services.json         # Android Firebase backup
└── GoogleService-Info.plist     # iOS Firebase backup
```

### Modified Files

- `android/app/build.gradle` (or `.kts`) - Signing configuration added
- `android/app/build.gradle.backup` - Backup of original file

---  



## ⚙️ Advanced Customization

### Change Keystore Password

Modify the `password` value in the `CONFIG` section:

```python
"password": "your-strong-password-here",
```

### Adjust Certificate Validity

Change the `validity_days` value (in days):

```python
"validity_days": 10000,  # ~27 years
```

### Custom Keystore Path

Modify `keystore_dir`:

```python
"keystore_dir": "your-custom-path",
```

---

## 🔄 Working with Firebase

### If You Have Firebase in Your Project

The script automatically:

1. ✅ Searches for Firebase files (`google-services.json` and `GoogleService-Info.plist`)
2. ✅ Backs them up to `necessary_files/`
3. ✅ Adds them to `.gitignore` (automatic protection)
4. ✅ Creates `firebase-info.txt` with backup details

### Restore Firebase Files

After cloning the project or on a new machine:

```bash
# On Windows
restore_firebase.bat

# On macOS/Linux
bash restore_firebase.sh
```

---

## 🔒 Security & Protection

### ⚠️ Important Security Notes

| File | Protected | Action |
|------|-----------|--------|
| `upload-keystore.jks` | ❌ **Not Protected** | Keep secure backup |
| `key.properties` | ✅ Protected by Git | **Never Share** |
| `google-services.json` | ✅ Protected by Git | Contains API Keys |
| `GoogleService-Info.plist` | ✅ Protected by Git | Contains API Keys |

### Security Best Practices

1. **Add Keystore to .gitignore** (if not already present):
   ```gitignore
   necessary_files/upload-keystore.jks
   necessary_files/key.properties
   necessary_files/google-services.json
   necessary_files/GoogleService-Info.plist
   ```

2. **Keep a Secure Backup** of `upload-keystore.jks` (🔴 Critical!)

3. **Use a Strong Password** for your Keystore

4. **Never Share** any files from `necessary_files/` via email or internet

---

## 🛠️ Troubleshooting

### ❌ Error: "keytool not found"

**Solution:**
- Install Java JDK from [oracle.com](https://www.oracle.com/java/technologies/downloads/)
- On Windows: Add JDK path to Environment Variables
  - `C:\Program Files\Java\jdk-XX\bin`


## 📚 Project Structure

```
project-root/
├── setup_keystore.py                # Main script
├── necessary_files/                 # Generated files
│   ├── upload-keystore.jks
│   └── key.properties
├── android/
│   └── app/
│       ├── build.gradle             # Modified
│       └── build.gradle.backup      # Backup
└── .gitignore                       # Updated
```

---

## 📞 Resources & Documentation

- 📖 [Flutter Official Documentation](https://docs.flutter.dev/deployment/android)
- 🔑 [Android App Signing Guide](https://developer.android.com/studio/publish/app-signing)
- 🔥 [Firebase Setup Documentation](https://firebase.google.com/docs/android/setup)

---

## 📝 License & Usage

This script is open-source and free to use. Feel free to use and modify it! 🚀

---

**This script was created to save time and effort from complex Keystore creation steps.**

> 💡 **Tip**: Keep this README in your project and reference it whenever needed!
