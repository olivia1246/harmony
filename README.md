attempt to rewrite in powershell to allow running from memory for more efficiency and auto update if using the below command on the remote computer (that you own or have permission to use this on!)

powershell -W Hidden -EP Bypass -C "IEX (IWR 'https://example.com/harmony.ps1' -UseBasicParsing);exit"
