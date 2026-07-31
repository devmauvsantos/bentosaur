#!/usr/bin/env bash

set -euo pipefail

project_file="${1:-build/ios/Bentosaur.xcodeproj/project.pbxproj}"

if [[ ! -f "$project_file" ]]; then
  echo "Missing generated Xcode project: $project_file" >&2
  exit 1
fi

require_setting() {
  local expected="$1"
  local message="$2"
  if ! rg --fixed-strings --quiet "$expected" "$project_file"; then
    echo "$message" >&2
    exit 1
  fi
}

reject_marker() {
  local forbidden="$1"
  if rg --fixed-strings --quiet "$forbidden" "$project_file"; then
    echo "Forbidden Mellow signing marker found: $forbidden" >&2
    exit 1
  fi
}

require_setting \
  "DEVELOPMENT_TEAM = 53RJ43876F;" \
  "Generated project is not locked to the personal Apple team."
require_setting \
  "PRODUCT_BUNDLE_IDENTIFIER = com.mauvsantos.bentosaur;" \
  "Generated project has the wrong bundle identifier."
require_setting \
  "CODE_SIGN_STYLE = \"Automatic\";" \
  "Generated project is not using Xcode automatic signing."
require_setting \
  "CODE_SIGN_IDENTITY = \"Apple Development\";" \
  "Debug configuration is not using an Apple Development identity."
require_setting \
  "PROVISIONING_PROFILE_SPECIFIER = \"\";" \
  "Generated project unexpectedly pins a provisioning profile."

for marker in \
  "274NNU52S8" \
  "655H347X58" \
  "mauricio@mellow.kids" \
  "Mellow Kids" \
  "NYMU5SBURP" \
  "5FU6XCM55P"
do
  reject_marker "$marker"
done

echo "Generated Xcode personal-signing contract: PASS"
