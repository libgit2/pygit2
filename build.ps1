$ErrorActionPreference = 'Stop'

$LIBGIT2_VERSION = $env:LIBGIT2_VERSION
$LIBGIT2_SRC = $env:LIBGIT2_SRC
if (-not $LIBGIT2_SRC) {
    $LIBGIT2_SRC = "build/libgit2_src"
}

# Prefer CMAKE_INSTALL_PREFIX, then LIBGIT2, then the default Program Files location.
$INSTALL_PREFIX = $env:CMAKE_INSTALL_PREFIX
if (-not $INSTALL_PREFIX) {
    $INSTALL_PREFIX = $env:LIBGIT2
}
if (-not $INSTALL_PREFIX) {
    $INSTALL_PREFIX = "$env:ProgramFiles\libgit2"
}

# Use cached dependencies if they match the requested version.
if ((Test-Path -Path "$INSTALL_PREFIX\versions.txt") -and $LIBGIT2_VERSION) {
    $cached = Get-Content "$INSTALL_PREFIX\versions.txt"
    $matches = $cached | Select-String "^LIBGIT2_VERSION=$LIBGIT2_VERSION$"
    if ($matches) {
        Write-Host "Using cached dependencies"
        exit 0
    }
}

if (!(Test-Path -Path "build")) {
    # in case the pygit2 package build/ workspace has not been created by cibuildwheel yet
    mkdir build
}
if (Test-Path -Path "$LIBGIT2_SRC") {
    Set-Location "$LIBGIT2_SRC"
    # for local runs, reuse build/libgit_src if it exists
    if (Test-Path -Path build) {
        # purge previous build env (likely for a different arch type)
        Remove-Item -Recurse -Force build
    }
    # ensure we are checked out to the right version
    git fetch --depth=1 --tags
    git checkout "v$LIBGIT2_VERSION"
} else {
    # from a fresh run (like in CI)
    git clone --depth=1 -b "v$LIBGIT2_VERSION" https://github.com/libgit2/libgit2.git $LIBGIT2_SRC
    Set-Location "$LIBGIT2_SRC"
}
cmake -B build -S . -DBUILD_TESTS=OFF -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX"
cmake --build build/ --config=Release --target install

# Record version so the cache can be reused.
"LIBGIT2_VERSION=$LIBGIT2_VERSION" | Set-Content "$INSTALL_PREFIX\versions.txt" -NoNewline
