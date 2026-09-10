# AUR packaging

`PKGBUILD` and `.SRCINFO` for the `hatchment` AUR package. Verified with
`makepkg -f`: builds clean, 58K, and installs the launcher, icon, desktop entry,
licence and README.

## Publishing an update

Pushing to the AUR needs an account at <https://aur.archlinux.org> with an SSH
public key registered on the profile page. The AUR only accepts these two files
plus any patches — never the source itself.

```bash
git clone ssh://aur@aur.archlinux.org/hatchment.git aur-hatchment
cd aur-hatchment
cp ../packaging/aur/{PKGBUILD,.SRCINFO} .
git add PKGBUILD .SRCINFO
git commit -m "hatchment 0.1.0-1"
git push
```

## For a new version

1. Tag and release upstream, so the tarball URL resolves.
2. Bump `pkgver` in `PKGBUILD` and reset `pkgrel=1`.
3. Refresh the checksum:
   `updpkgsums` — or `curl -sSL <tarball> | sha256sum`.
4. Regenerate the metadata: `makepkg --printsrcinfo > .SRCINFO`.
5. Rebuild before pushing: `makepkg -f`.

Step 4 is the one people forget. The AUR reads `.SRCINFO`, not `PKGBUILD`, so a
stale one publishes the previous version's metadata against the new files.
