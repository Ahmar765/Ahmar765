# Activate Ahmar765's animated profile

1. Create the **public** repository `Ahmar765/Ahmar765` on GitHub, or open it if it already exists.
2. Copy this folder's contents into that repository, including `.github/workflows/update-profile-art.yml`. Keep any unrelated existing files. Commit to `main`.
3. Open **Actions → Update profile art → Run workflow**. The initial push also triggers the workflow when these files are added.
4. Wait for a successful run. It downloads your public GitHub avatar, converts it into an ASCII portrait, fetches your real contributions, and commits the SVGs. The workflow uses GitHub's built-in repository token; you do not need a personal access token or external stats service.

The checked-in first-run graph explicitly says it is awaiting live data. It contains no invented contribution counts. The initial ASCII monogram is replaced with your actual GitHub avatar on the first workflow run. If your avatar is a logo or identicon, its ASCII version will also be a logo or identicon.

## Use your own portrait

Save your photo as `assets/avatar.png` before running the workflow. A tightly cropped, well-lit portrait on a simple pale background works best. The script keeps an existing portrait. To use another local path, edit `portrait` in `profile.json`; update the workflow's avatar path check and staged asset path too.

## Edit your details

Edit `profile.json` for your name, role and stack. Update the README's visible tagline and image alt text if you change those details. Your email address is intentionally omitted from these public files.

## Generate locally

```powershell
python -m pip install -r scripts/requirements.txt
python scripts/build_profile.py --avatar --fetch
```

To render using an existing portrait and saved calendar without accessing the network:

```powershell
python scripts/build_profile.py
```

The cron requests a refresh daily at 06:17 UTC; GitHub may delay scheduled runs. The public calendar HTML is an undocumented endpoint and can change; malformed or incomplete responses fail the workflow before any artwork is committed, preserving the last good graph. GitHub controls whether private contribution totals are visible, image caching, and animation playback. SVGs have a readable final-state fallback when animations are disabled.

Design inspired by [AVIVASHISHTA29's profile](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29); generated independently for Ahmar765.
