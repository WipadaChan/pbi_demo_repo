
#****************
#------------------------------------------------------
# --> PBI Connection
#------------------------------------------------------ 
Write-Host " PBI credentials ..." -ForegroundColor Yellow -BackgroundColor DarkGreen

## PBI credentials 

$password = "XXXXXX" | ConvertTo-SecureString -asPlainText -Force
$username = "XXXX@contoso.com" 
$credential = New-Object System.Management.Automation.PSCredential($username, $password)

## PBI connect 

Connect-PowerBIServiceAccount -Credential $credential

# Login-PowerBI


$pbiURL = 'https://api.powerbi.com/v1.0/myorg/admin/groups?$expand=users&$top=500'

## API call

$headers = Get-PowerBIAccessToken
$resultJson = Invoke-RestMethod -Headers $headers -Uri  $pbiURL

## Filter only premium Workspace 
$tmp = $resultJson.Value.Where{$_.isOnDedicatedCapacity -match 'True'}  
$tmp = $tmp.Where{$_.type -match 'Workspace'}

foreach ($WorkspaceId in $tmp) {

$data += $WorkspaceId.users| 
    SELECT @{n='WorkspaceId';e={$WorkspaceId.id}}, 
            @{n='Workspace';e={$WorkspaceId.name}}, 
            emailAddress, 
            principalType, 
            @{n='type';e={$WorkspaceId.type}}, 
            @{n='state';e={$WorkspaceId.state}}

}

$data | export-csv "c:\PowerBIGroupMembers.csv" -NoTypeInformation