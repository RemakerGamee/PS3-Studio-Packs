# Adding your patch pack

## 1. Make the pack in the Studio

- **Patch packs > Make pack from a patch folder…** if you have a folder of numbered `.patch` files, or
- write a `pack.json` by hand (format: PATCH-PACKS.md in the Studio folder).

Install it and build your game with it once, to make sure every patch applies.

## 2. Export it

Select your pack and press **Share selected pack…**. The Studio saves a ZIP and shows a ready-made list entry with its SHA-256.

## 3. Upload the ZIP

Create a release on **your own** GitHub repository (for example tag `pack-1.0.0`) and attach the ZIP. Copy the file's download address; it looks like:

```
https://github.com/<you>/<repo>/releases/download/<tag>/<file>.zip
```

## 4. Add your entry here

1. Open `index.json` in this repository and click the pencil (Edit).
2. Add your entry inside `"packs": [ ... ]`, with the download address in `"url"`. Put a comma between entries.
3. Click **Propose changes**, then **Create pull request**.

An automatic check downloads your ZIP, confirms the SHA-256 and checks `pack.json`. Once it passes and the pack is reviewed, it shows up in everyone's Studio.

```json
{
  "id": "kz3-example",
  "name": "Killzone 3 example pack",
  "version": "1.0.0",
  "author": "your name",
  "homepage": "https://github.com/you/your-port",
  "license": "MIT",
  "description": "What it fixes, which update version it needs.",
  "title_ids": ["BCUS98234", "BCES01007"],
  "url": "https://github.com/you/your-port/releases/download/pack-1.0.0/kz3-example-1.0.0.zip",
  "sha256": "<from the Share window>"
}
```

## Updating your pack

Raise `version` in your `pack.json`, export again, upload the new ZIP, and open a pull request changing your entry's `version`, `url` and `sha256`. Studio users see "update" next to your pack.
