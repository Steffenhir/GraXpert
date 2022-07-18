#!/bin/bash
commit=$(git log -1 --format='%H')
tag=$(git tag -n --points-at $commit)
IFS=' ' read -r version release <<< $tag

if [[ $release != "" && $version != "" ]]; 
then
  sed -i'.bak' "s/RELEASE/$release/" ./src/version.py
  sed -i'.bak' "s/SNAPSHOT/$version/" ./src/version.py
  sed -i'.bak' "s/RELEASE/$release/" ./GraXpert-macos-x86_64.spec
  sed -i'.bak' "s/SNAPSHOT/$version/" ./GraXpert-macos-x86_64.spec
else
  echo "WARNING: Could not retrieve git release tag"
fi
