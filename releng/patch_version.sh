#!/bin/bash

set -e

# Get the tag and its first annotation line for this commit, if any
tag_info=$(git tag -n --points-at HEAD)

if [[ -n "$tag_info" ]]; 
then
  # Tag exactly matches the current commit

  # Read lines of the form "3.0.0b1 ReleaseName" into version and release
  IFS=' ' read -r version release <<< "$tag_info"

  # If the tag has no annotation, just use python PEP 440 style versioning
  if [[ -z "$release" ]]; then
    release="1"
  fi

  echo "INFO: Found tag on current commit. Using $version and $release"
  
else
  # No tag on the current commit - make something with the SHA

  # Find the most recent tag on this branch. Suppress errors if no tags exist.
  most_recent_tag=$(git describe --tags --abbrev=0 2>/dev/null)

  # If the tag is already a dev tag, strip the .dev* part for the new version
  most_recent_tag_base=${most_recent_tag%%.dev*}

  # Get the current UTC timestamp in YYMMDDHHMMSS format
  timestamp=$(date -u +%y%m%d%H%M%S)

  if [[ -n "$most_recent_tag_base" ]]; then
    # Construct version from the most recent tag and the timestamp
    version="${most_recent_tag_base}.dev${timestamp}"
  else
    # Fallback if no tags exist in the repo's history at all.
    echo "WARNING: No ancestor tags found. Using '0.0.0' as base."
    version="0.0.0.dev${timestamp}"
  fi
  
  # Construct the development release name
  release="dev-${timestamp}"
  
  echo "INFO: No tag found on current commit. Using $version instead."
fi

if [[ $release != "" && $version != "" ]]; 
then
  cp ./releng/version-tmpl.py ./graxpert/version.py
  # Note: -i'.bak' is _required_ for BSD sed (macOS)
  sed -i'.bak' "s^RELEASE^$release^" ./graxpert/version.py
  sed -i'.bak' "s^SNAPSHOT^$version^" ./graxpert/version.py
  cp ./releng/GraXpert-macos-x86_64-tmpl.spec ./GraXpert-macos-x86_64.spec
  sed -i'.bak' "s^RELEASE^$release^" ./GraXpert-macos-x86_64.spec
  sed -i'.bak' "s^SNAPSHOT^$version^" ./GraXpert-macos-x86_64.spec
else
  echo "WARNING: Could not retrieve git release tag"
fi
