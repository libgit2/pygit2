if (!(Test-Path -Path "build")) {
    # in case the pygit2 package build/ workspace has not been created by cibuildwheel yet
    mkdir build
}
if (Test-Path -Path "$env:LIBGIT2_SRC") {
    Set-Location "$env:LIBGIT2_SRC"
    # for local runs, reuse build/libgit_src if it exists
    if (Test-Path -Path build) {
        # purge previous build env (likely for a different arch type)
        Remove-Item -Recurse -Force build
    }
    # ensure we are checked out to the right version
    git fetch --depth=1 --tags
    git checkout "v$env:LIBGIT2_VERSION"
} else {
    # from a fresh run (like in CI)
    git clone --depth=1 -b "v$env:LIBGIT2_VERSION" https://github.com/libgit2/libgit2.git $env:LIBGIT2_SRC
    Set-Location "$env:LIBGIT2_SRC"
}
cmake -B build -S . -DBUILD_TESTS=OFF
cmake --build build/ --config=Release --target install
