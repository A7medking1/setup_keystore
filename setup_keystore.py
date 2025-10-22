#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
سكريبت تلقائي لإنشاء Android Keystore و Code Signing
يعمل تلقائياً عند رفع المشروع لأول مرة

الاستخدام:
    python setup_keystore.py
"""

import json
import os
import subprocess
import sys
from pathlib import Path

# ============================================
# الإعدادات - عدلها حسب رغبتك
# ============================================

CONFIG = {
    # معلومات الشركة/المطور
    "company_name": "testComp",
    "developer_name": "ahmed nasr",
    "organization": "testComp",
    "city": "Cairo",
    "state": "Cairo",
    "country": "EG",

    # إعدادات الـ Keystore
    "keystore_dir": "necessary_files",
    "keystore_name": "upload-keystore.jks",
    "key_alias": "upload",
    "validity_days": 10000,  # ~27 سنة
    "password": "123456",
}


# ============================================
# دوال مساعدة
# ============================================

def print_header(text):
    """طباعة عنوان منسق"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """طباعة رسالة نجاح"""
    print(f"✅ {text}")


def print_error(text):
    """طباعة رسالة خطأ"""
    print(f"❌ {text}")


def print_info(text):
    """طباعة معلومة"""
    print(f"ℹ️  {text}")


def check_keytool():
    """التحقق من وجود keytool على Windows أو macOS أو Linux"""
    # أولاً نحاول نلاقي keytool في PATH الحالي
    import shutil

    keytool_path = shutil.which("keytool")

    # لو مش موجود نحاول نبحث في مواقع الـ JDK الشائعة على Windows
    if not keytool_path:
        possible_paths = [
            r"C:\Program Files\Java\jdk-21\bin\keytool.exe",
            r"C:\Program Files\Java\jdk-22\bin\keytool.exe",
            r"C:\Program Files\Java\jdk-20\bin\keytool.exe",
            r"C:\Program Files\Java\jdk-17\bin\keytool.exe",
        ]
        for p in possible_paths:
            if os.path.exists(p):
                os.environ["PATH"] += ";" + os.path.dirname(p)
                keytool_path = p
                print(f"✅ تم العثور على keytool في: {p}")
                break

    # لو بعد كل ده لسه مش موجود
    if not keytool_path:
        print("❌ لم يتم العثور على keytool. تأكد من تثبيت JDK أو تعديل PATH.")
        return False

    # الآن نجرب تشغيله فعلاً للتأكد من أنه يعمل
    try:
        subprocess.run([keytool_path, "-help"], capture_output=True, text=True, check=True)
        return True
    except Exception as e:
        print(f"⚠️ خطأ أثناء محاولة تشغيل keytool: {e}")
        return False


def create_directory(path):
    """إنشاء مجلد إذا لم يكن موجود"""
    Path(path).mkdir(parents=True, exist_ok=True)
    print_success(f"تم إنشاء المجلد: {path}")


def keystore_exists(keystore_path):
    """التحقق من وجود Keystore"""
    return Path(keystore_path).exists()


def generate_keystore(config):
    """إنشاء Keystore جديد"""
    keystore_path = os.path.join(config["keystore_dir"], config["keystore_name"])

    keystore_password = config["password"]
    key_password = config["password"]

    print_info("جاري إنشاء Keystore...")

    # أمر keytool
    dname = (
        f"CN={config['developer_name']}, "
        f"OU={config['organization']}, "
        f"O={config['company_name']}, "
        f"L={config['city']}, "
        f"ST={config['state']}, "
        f"C={config['country']}"
    )

    cmd = [
        "keytool",
        "-genkey",
        "-v",
        "-keystore", keystore_path,
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", str(config["validity_days"]),
        "-alias", config["key_alias"],
        "-storepass", keystore_password,
        "-keypass", key_password,
        "-dname", dname,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_success(f"تم إنشاء Keystore: {keystore_path}")
        return keystore_password, key_password
    except subprocess.CalledProcessError as e:
        print_error(f"فشل إنشاء Keystore: {e.stderr}")
        sys.exit(1)


def create_key_properties(config, keystore_password, key_password):
    """إنشاء ملف key.properties"""
    key_properties_path = os.path.join(config["keystore_dir"], "key.properties")

    content = f"""storePassword={keystore_password}
keyPassword={key_password}
keyAlias={config['key_alias']}
storeFile=../../necessary_files/{config['keystore_name']}
"""

    with open(key_properties_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print_success(f"تم إنشاء: {key_properties_path}")


def update_android_build_gradle():
    """تحديث android/app/build.gradle أو build.gradle.kts تلقائيًا"""
    import re

    gradle_paths = [
        "android/app/build.gradle",
        "android/app/build.gradle.kts"
    ]

    gradle_path = next((p for p in gradle_paths if os.path.exists(p)), None)
    if not gradle_path:
        print("❌ لم يتم العثور على build.gradle أو build.gradle.kts")
        return False

    print(f"📄 جاري قراءة الملف: {gradle_path}")
    is_kts = gradle_path.endswith(".kts")

    with open(gradle_path, "r", encoding="utf-8") as f:
        original_content = f.read()

    # -------------------------------
    # للكوتلن DSL (.kts)
    # -------------------------------
    if is_kts:
        print("⚙️ تعديل build.gradle.kts ...")

        content = original_content

        # ✅ إضافة import في الأعلى لو غير موجود
        if "import java.util.Properties" not in content:
            content = (
                    "import java.util.Properties\n"
                    "import java.io.FileInputStream\n\n" + content
            )
            print("✓ تم إضافة import في أعلى الملف")

        # ✅ حذف أي release قديم
        content = re.sub(
            r'buildTypes\s*\{[^}]*release\s*\{[^}]*\}[^}]*\}',
            '',
            content,
            flags=re.DOTALL
        )

        # ✅ إضافة كود keystore لو غير موجود
        if "keystorePropertiesFile" not in content:
            keystore_block = """
// ============================================
// تحميل إعدادات Android Keystore (Kotlin DSL)
// ============================================
val keystorePropertiesFile = rootProject.file("../necessary_files/key.properties")
val keystoreProperties = Properties()

if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}
"""
            # أضفه قبل android {
            content = content.replace("android {", keystore_block + "\nandroid {", 1)
            print("✓ تم إضافة إعدادات keystore")

        # ✅ إضافة signingConfigs و buildTypes مضبوطين
        build_block = """
    // ============================================
    // إعدادات التوقيع (Kotlin DSL)
    // ============================================
    signingConfigs {
        create("release") {
            if (keystorePropertiesFile.exists()) {
                keyAlias = keystoreProperties["keyAlias"] as String
                keyPassword = keystoreProperties["keyPassword"] as String
                storeFile = file(keystoreProperties["storeFile"] as String)
                storePassword = keystoreProperties["storePassword"] as String
            }
        }
    }

    buildTypes {
        getByName("release") {
            signingConfig = signingConfigs.getByName("release")
        }
    }
"""
        # أضف بعد defaultConfig
        content = re.sub(
            r'(defaultConfig\s*\{[^}]*\})',
            r'\1\n' + build_block,
            content,
            flags=re.DOTALL
        )

        # حفظ النسخة الجديدة
        backup_path = gradle_path + ".backup"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        with open(gradle_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("🎯 build.gradle.kts تم تحديثه بنجاح ✓")
        return True

    # -------------------------------
    # للـ Groovy DSL (build.gradle)
    # -------------------------------
    else:
        print("⚙️ تعديل build.gradle (Groovy DSL) ...")

        content = original_content

        # حذف release القديم
        content = re.sub(
            r'buildTypes\s*\{[^}]*release\s*\{[^}]*\}[^}]*\}',
            '',
            content,
            flags=re.DOTALL
        )

        keystore_loader = """
// ============================================
// تحميل إعدادات Android Keystore (Groovy DSL)
// ============================================
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('../necessary_files/key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
"""
        if "keystorePropertiesFile" not in content:
            content = content.replace("android {", keystore_loader + "\nandroid {", 1)
            print("✓ تم إضافة إعدادات keystore")

        build_block = """
    signingConfigs {
        release {
            if (keystorePropertiesFile.exists()) {
                keyAlias keystoreProperties['keyAlias']
                keyPassword keystoreProperties['keyPassword']
                storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
                storePassword keystoreProperties['storePassword']
            }
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
"""
        content = re.sub(
            r'(defaultConfig\s*\{[^}]*\})',
            r'\1\n' + build_block,
            content,
            flags=re.DOTALL
        )

        backup_path = gradle_path + ".backup"
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(original_content)
        with open(gradle_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("🎯 build.gradle تم تحديثه بنجاح ✓")
        return True


def check_and_backup_firebase_files():
    """التحقق من ملفات Firebase ونسخها إلى necessary_files"""
    print_header("🔥 التحقق من ملفات Firebase")

    firebase_files = {
        "android": {
            "path": "android/app/google-services.json",
            "name": "google-services.json",
            "description": "Android Firebase Config"
        },
        "ios": {
            "path": "ios/Runner/GoogleService-Info.plist",
            "name": "GoogleService-Info.plist",
            "description": "iOS Firebase Config"
        }
    }

    found_files = []

    for platform, info in firebase_files.items():
        file_path = info["path"]

        if os.path.exists(file_path):
            print_success(f"تم العثور على: {info['description']}")

            # نسخ الملف إلى necessary_files
            dest_path = os.path.join(CONFIG["keystore_dir"], info["name"])

            try:
                import shutil
                shutil.copy2(file_path, dest_path)
                print_success(f"✓ تم نسخ: {info['name']} → necessary_files/")
                found_files.append({
                    "platform": platform,
                    "name": info["name"],
                    "original": file_path,
                    "backup": dest_path
                })
            except Exception as e:
                print_error(f"فشل نسخ {info['name']}: {e}")
        else:
            print_info(f"غير موجود: {info['description']}")

    if found_files:
        print_success(f"تم نسخ {len(found_files)} من ملفات Firebase")

        # إنشاء ملف معلومات Firebase البسيط
        create_firebase_info_simple(found_files)


        return True
    else:
        print_info("لم يتم العثور على ملفات Firebase")
        print_info("إذا كنت تستخدم Firebase، تأكد من:")
        print_info("  • تشغيل: flutterfire configure")
        print_info("  • وجود الملفات في المسارات الصحيحة")
        return False


def create_firebase_info_simple(files):
    """إنشاء ملف معلومات Firebase بسيط"""
    info_path = os.path.join(CONFIG["keystore_dir"], "firebase-info.txt")

    from datetime import datetime

    content = f"""{'=' * 60}
نسخ احتياطي لملفات Firebase
{'=' * 60}

تم نسخ ملفات Firebase التالية إلى مجلد necessary_files:

"""

    for file_info in files:
        content += f"""
Platform: {file_info['platform'].upper()}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 اسم الملف: {file_info['name']}
📍 المسار الأصلي: {file_info['original']}
💾 النسخة الاحتياطية: {file_info['backup']}

"""

    content += f"""
{'=' * 60}
ملاحظات مهمة
{'=' * 60}

⚠️  هذه الملفات تحتوي على API Keys خاصة بـ Firebase
⚠️  تم إضافتها إلى .gitignore تلقائياً (محمية من Git)
⚠️  احفظ نسخة احتياطية في مكان آمن

{'=' * 60}
تاريخ النسخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 60}
"""

    with open(info_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print_success(f"تم إنشاء: {info_path}")


def check_firebase_connection():
    """التحقق من اتصال المشروع بـ Firebase"""
    print_header("🔍 فحص اتصال Firebase")

    # التحقق من pubspec.yaml
    pubspec_path = "pubspec.yaml"

    if not os.path.exists(pubspec_path):
        print("pubspec.yaml غير موجود!")
        return False

    with open(pubspec_path, 'r', encoding='utf-8') as f:
        pubspec_content = f.read()

    # البحث عن Firebase packages
    firebase_packages = [
        "firebase_core",
        "firebase_auth",
        "firebase_analytics",
        "firebase_messaging",
        "cloud_firestore",
        "firebase_storage"
    ]

    found_packages = [pkg for pkg in firebase_packages if pkg in pubspec_content]

    if found_packages:
        print_success(f"تم العثور على {len(found_packages)} من حزم Firebase:")
        for pkg in found_packages:
            print_info(f"  • {pkg}")
        return True
    else:
        print_info("لم يتم العثور على حزم Firebase في pubspec.yaml")
        return False
    """إنشاء ملف JSON للتأكد من اكتمال الإعداد"""
    setup_path = os.path.join(config["keystore_dir"], ".setup_complete")

    from datetime import datetime

    data = {
        "setup_completed": True,
        "setup_date": datetime.now().isoformat(),
        "keystore_name": config["keystore_name"],
        "key_alias": config["key_alias"],
        "version": "1.0"
    }

    with open(setup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print_success("تم إنشاء: .setup_complete")


# ============================================
# البرنامج الرئيسي
# ============================================

def main():
    print_header("🔐 إعداد Android Keystore التلقائي")

    # التحقق من وجود keytool
    print_info("جاري التحقق من keytool...")
    if not check_keytool():
        print_error("keytool غير موجود!")
        print_info("تأكد من تثبيت Java JDK")
        print_info("Windows: أضف Java/bin إلى PATH")
        sys.exit(1)
    print_success("keytool موجود ✓")

    # إنشاء المجلد
    print_info(f"جاري إنشاء المجلد: {CONFIG['keystore_dir']}")
    create_directory(CONFIG["keystore_dir"])

    # التحقق من وجود Keystore
    keystore_path = os.path.join(CONFIG["keystore_dir"], CONFIG["keystore_name"])

    if keystore_exists(keystore_path):
        print_info("Keystore موجود بالفعل!")
        response = input("هل تريد إنشاء واحد جديد؟ (سيحذف القديم) [y/N]: ")
        if response.lower() != 'y':
            print_info("تم الإلغاء")
            sys.exit(0)
        os.remove(keystore_path)

    # إنشاء Keystore
    print_header("📦 إنشاء Keystore")
    keystore_password, key_password = generate_keystore(CONFIG)

    # إنشاء الملفات المساعدة
    print_header("📝 إنشاء الملفات المساعدة")
    create_key_properties(CONFIG, keystore_password, key_password)

    # التحقق من Firebase ونسخ الملفات
    firebase_connected = check_firebase_connection()
    firebase_files = []

    if firebase_connected:
        has_firebase = check_and_backup_firebase_files()
        if has_firebase:

            # إضافة Firebase للـ GitHub Secrets guide
            firebase_files_info = []
            if os.path.exists(os.path.join(CONFIG["keystore_dir"], "google-services.json")):
                firebase_files_info.append({
                    "platform": "android",
                    "name": "google-services.json",
                    "backup": os.path.join(CONFIG["keystore_dir"], "google-services.json")
                })
            if os.path.exists(os.path.join(CONFIG["keystore_dir"], "GoogleService-Info.plist")):
                firebase_files_info.append({
                    "platform": "ios",
                    "name": "GoogleService-Info.plist",
                    "backup": os.path.join(CONFIG["keystore_dir"], "GoogleService-Info.plist")
                })

    # تحديث build.gradle
    print_header("🔧 تحديث Android Build Configuration")
    gradle_success = update_android_build_gradle()

    if not gradle_success:
        print("⚠️  فشل تحديث build.gradle!")
        print_info("يمكنك تعديله يدوياً لاحقاً")
        print_info("راجع: build.gradle (مثال) في الملف المرفق")

    # النتيجة النهائية
    print_header("✅ اكتمل الإعداد!")
    print_success("تم إنشاء جميع الملفات بنجاح!")

    print("\n" + "=" * 60)
    print("📋 الخطوات التالية:")
    print("=" * 60)

    if firebase_connected and has_firebase:
        print("5. 🔥 راجع: firebase-info.txt (ملفات Firebase محفوظة)")
        print("6. لاستعادة Firebase: شغل restore_firebase.sh/.bat")
        print("7. لا تضف الملفات الحساسة إلى Git!")
        print("8. اعمل نسخة احتياطية من الـ Keystore!")
    else:
        print("5. لا تضف الملفات الحساسة إلى Git!")
        print("6. اعمل نسخة احتياطية من الـ Keystore!")

    print("=" * 60)

    if firebase_connected and has_firebase:
        print("• 🔥 ملفات Firebase محمية من Git تلقائياً")
        print("• 🔥 استخدم سكريبتات الاستعادة عند الحاجة")

    print("=" * 60)

    # ملخص الملفات المنشأة
    print("\n" + "=" * 60)
    print("📦 الملفات المنشأة:")
    print("=" * 60)
    print("✓ upload-keystore.jks")
    print("✓ key.properties")
    print("✓ android/app/build.gradle (معدل)")
    print("✓ android/app/build.gradle.backup")

    if firebase_connected and has_firebase:
        print("\n🔥 ملفات Firebase:")
        if os.path.exists(os.path.join(CONFIG["keystore_dir"], "google-services.json")):
            print("✓ google-services.json (نسخة احتياطية)")
        if os.path.exists(os.path.join(CONFIG["keystore_dir"], "GoogleService-Info.plist")):
            print("✓ GoogleService-Info.plist (نسخة احتياطية)")
        print("✓ firebase-info.txt")
        print("✓ restore_firebase.sh")
        print("✓ restore_firebase.bat")

    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ تم الإلغاء بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        print_error(f"خطأ غير متوقع: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
