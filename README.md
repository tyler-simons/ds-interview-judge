# DS Interview Judge

Original data science interview practice: judge whether the AI answer is right or wrong.

## Passcode gate (v3.1.0)
The first visit on a device shows a 6-digit passcode screen. Once the code is entered correctly, the device is remembered in localStorage (`dsjudge_device_ok`). Settings → "Forget this device" clears that flag.
**This is a casual gate on a public static site, not real security.** Only a salted PBKDF2-SHA256 hash is stored in the code. However, the page and questions are public, and anyone with devtools can bypass it. Your stats stay protected by the GitHub token, which only lives on your device.
