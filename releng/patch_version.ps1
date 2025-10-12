# Get the tag and its first annotation line for this commit, if any
$tagInfo = git tag -n --points-at HEAD

if (-not [string]::IsNullOrWhiteSpace($tagInfo)) {
    # --- CASE 1: Tag exists on the current commit ---
    # Split the tag info string "3.0.0b1 ReleaseName" into version and release
    $version, $release = ($tagInfo -split ' ', 2).Trim()

    # If the tag has no annotation, default to "1" for PEP 440 style
    if ([string]::IsNullOrWhiteSpace($release)) {
        $release = "1"
    }

    Write-Output "INFO: Found tag on current commit. Using $version and $release"
} else {
    # --- CASE 2: No tag on the current commit ---
    # Find the most recent tag on this branch. Suppress errors if no tags exist.
    $mostRecentTag = git describe --tags --abbrev=0 2>$null
    
    if (-not [string]::IsNullOrWhiteSpace($mostRecentTag)) {
        # If a tag exists, create a dev version based on it.
        # Get the number of commits since the most recent tag.
        $commitCount = (git rev-list $mostRecentTag..HEAD --count).Trim()
        # Strip any existing .dev part from the tag for the new version base.
        $mostRecentTagBase = $mostRecentTag -replace '\.dev.*$'
        # Construct a PEP 440 compliant dev version.
        $version = "${mostRecentTagBase}.dev${commitCount}"
        $release = "dev-${commitCount}"
    } else {
        # Fallback if no tags exist in the repo's history at all
        $commitCount = (git rev-list --count HEAD).Trim()
        Write-Warning "No ancestor tags found. Using '0.0.0' as base."
        $version = "0.0.0.dev${commitCount}"
        $release = "dev-${commitCount}"
    }

    Write-Output "INFO: No tag found on current commit. Using $version instead."
}

# --- Perform substitution with the determined version and release ---
if ((-not [string]::IsNullOrWhiteSpace($version)) -and (-not [string]::IsNullOrWhiteSpace($release))) {

    # Define template and destination files
    $filesToPatch = @{
        ".\releng\version-tmpl.py"                  = ".\graxpert\version.py";
        ".\releng\GraXpert-macos-x86_64-tmpl.spec" = ".\GraXpert-macos-x86_64.spec";
    }
    
    foreach ($template in $filesToPatch.Keys) {
        $destination = $filesToPatch[$template]
        if (Test-Path $template) {
            # Copy template to destination
            Copy-Item -Path $template -Destination $destination -Force
            # Read the file once, perform both replacements, and write it back
            (Get-Content -Path $destination -Raw) -creplace 'RELEASE', $release -creplace 'SNAPSHOT', $version | Set-Content -Path $destination
        } else {
            Write-Warning "Template file not found, skipping: $template"
        }
    }
} else {
    Write-Warning "Could not retrieve git release tag"
    exit 1
}
