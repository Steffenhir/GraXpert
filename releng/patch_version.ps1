$commit = git log -1 --format='%H'
$tag = git tag -n --points-at $commit

if([string]::IsNullOrWhiteSpace($tag)) {
    Write-Output "WARNING: Could not retrieve git release tag (1)"
    Exit
}

$version,$release = ($tag -split ' ',2).Trim()

if((-not [string]::IsNullOrWhiteSpace($release)) -and
(-not [string]::IsNullOrWhiteSpace($version)))
{
(Get-Content -path .\src\version.py -Raw) -creplace 'RELEASE',$release | Set-Content -Path .\src\version.py
(Get-Content -path .\src\version.py -Raw) -creplace 'SNAPSHOT',$version | Set-Content -Path .\src\version.py
}
else
{
    Write-Output "WARNING: Could not retrieve git release tag (2)"
}
