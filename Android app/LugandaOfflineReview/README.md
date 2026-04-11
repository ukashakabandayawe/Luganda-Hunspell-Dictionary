# Luganda Offline Review (Android)

This folder contains a **Java** Android app project intended to run fully offline and embed `Luganda.dic` inside the APK.

## What you need to install (Windows)

1. **Android Studio** (includes Android SDK + build tools)
2. **JDK 17** (Android Studio can manage this automatically; if it asks, choose an embedded JDK)

## Open and build (APK)

1. Open Android Studio
2. **Open** this folder:
   - `E:\Luganda Hunspell Dictionary\Android app\LugandaOfflineReview`
3. Let it sync Gradle (first time may take a while)
4. Build a debug APK:
   - `Build` → `Build Bundle(s) / APK(s)` → `Build APK(s)`

Android Studio will show where it saved the APK.

## Embedded dictionary asset

The app expects this file to exist in:
- `app/src/main/assets/Luganda.dic`

If the file is present, the app shows a startup message confirming it can read it.

## App flow (offline review)

1. On the home screen, tap **Import Bundle** and choose the file you generated on the PC (a `.json.gz` bundle).
2. Tap **Open Queue** to see assigned stems.
3. Tap a stem and review one flag at a time:
   - Approve/Reject
   - Optional note
4. When done, go back to Home and export:
   - **Export Decisions (JSON)** → send this back to you for importing into `lgflagsite`
   - **Export Working Luganda.dic** → reviewer-specific `.dic` built from embedded `Luganda.dic` + approvals

## Launcher icon

The launcher icon is defined as a vector drawable and referenced in the manifest.
If your phone launcher caches icons, uninstall/reinstall the APK to see updates.
