# GitHub profile — binary headshot with featured projects (v3)

This version fixes the earlier unrecognizable portrait by **keeping the original uploaded photo visible** under the binary `0`/`1` character pattern. It does **not** generate or redraw a face. The attached PNGs display your actual facial features.

The original user-supplied photo is stored as `assets/headshot.png`; the small preview images are for viewing only. The generator uses Pillow to crop, gently color-adjust, and overlay the `0` and `1` glyphs, then outputs dark/light PNG files for reliable display on GitHub.

## Featured Projects
The main terminal card displays, in order, Visual Tizita, Lisan, NAEP,
and Nehas Digital Signage. The README also supplies clickable public project
links. Private source-code repositories are not exposed.

## Publish

1. Create a **public** repository named `nebiyumekonnen17` under your GitHub username `nebiyumekonnen17`: https://github.com/new. Do not initialize it with a README.
2. Extract this ZIP and upload the contents of this folder to the **root** of the new repository, including hidden `.github/workflows/update-profile.yml`, `README.md`, `generate_profile.py`, `assets/headshot.png`, `dark_mode.png`, and `light_mode.png`.
3. Once published, visit https://github.com/nebiyumekonnen17 — GitHub automatically displays `README.md` of this special same-name repository on your profile.
4. For real public statistics, open the repository's **Actions** tab, select **Refresh binary GitHub profile**, and choose **Run workflow**. Its daily schedule will continue when Actions are enabled and write permissions are allowed. The numbers in this preview are shown as dashes deliberately, to avoid inventing values.

## Run locally (optional)

```bash
python -m pip install 'Pillow>=10,<13'
python generate_profile.py --offline
```

Remove `--offline` to request public GitHub stats. Generated `dark_mode.png` and `light_mode.png` are the two files referenced by your GitHub profile README. In GitHub Actions, runs automatically fetch public numbers and commit changes to the PNG files.

## Change photo later

Replace `assets/headshot.png` with the desired high-resolution real photograph (same filename), then run `python generate_profile.py --offline`, commit the two PNG files, and push. No generated portraits or face-shape changes are used.
