# Karna Android Companion

The `android/` folder contains the first Karna Android companion application. It is a user-controlled Share Sheet target, not a background monitoring tool.

## What a person can do

From a supported Android app, choose **Share**, select **Karna**, review the selected content, and press **Scan with Karna**. The companion accepts:

- a message or URL from WhatsApp, a browser, an email app, or an SMS app;
- a JPG, PNG, or WEBP image from the gallery, camera, or file manager.

Karna displays the API's risk level, score, category, evidence, confidence, and recommended action. The result is advisory: the person decides whether to continue, close the content, report it, or ask for help.

## Privacy and platform boundary

WhatsApp, Telegram, Signal, Messenger, and other closed platforms are supported only when a person deliberately shares a message, link, or image to Karna. This companion does not directly read their conversations.

The first scan presents this notice: **“Only the content you choose to share is sent to Karna for analysis.”** The app requests only `INTERNET`; it does not request SMS, contacts, call-log, accessibility, notification-listener, storage-wide, or device-admin permissions. It does not retain shared content or results.

Automatic SMS monitoring is deliberately out of scope. A future design would need clear consent, platform-specific permissions, a privacy review, and Google Play policy review. It must not be added as a background-surveillance feature.

## Configure and run locally

1. Install Android Studio with a Java 17 Gradle JDK and Android SDK Platform 35.
2. Open the `android/` folder in Android Studio and allow it to sync the Gradle project.
3. Run the `app` configuration on an emulator or physical Android device.
4. In Karna, open Settings and verify the HTTPS API base URL. The default is `https://data-protactor.vercel.app/`.
5. In another Android app, choose Share and select Karna.

The mobile app never contains `OPENAI_API_KEY`, `VIRUSTOTAL_API_KEY`, or any other server secret. Those optional keys remain only in the Karna API deployment.

## Create a real Android download link

Do not publish an APK until it has been tested and signed.

1. Create a private signing key outside this repository. Never commit a keystore, passwords, or signing configuration.
2. Build and test a signed release APK or Android App Bundle in Android Studio.
3. Create a GitHub Release for a version tag such as `android-v0.1.0` and upload the signed APK as a release asset, or publish through Google Play.
4. Copy the HTTPS GitHub Release asset URL or Google Play URL.
5. Set `ANDROID_APP_DOWNLOAD_URL` in the Vercel project environment variables, then redeploy Karna.

Until that variable contains an HTTPS URL, the Karna dashboard intentionally displays a disabled “Download Karna for Android (coming soon)” control. It never points users to a fake download.

## Tests

The Android unit tests cover shared URL and text payload creation, unsupported and oversized image rejection, API-failure messaging, and safe rendering for an unexpected recommended action. Run them in Android Studio or with `./gradlew test` after Gradle is available on your machine.
