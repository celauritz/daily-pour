# The Daily Pour

Personal single-user habit tracker — talk / move / tidy, one small drill a day.
Ported from a Claude.ai artifact to a hosted PWA.

- **Single file:** `index.html` (vanilla JS, no build step)
- **Storage:** Firebase Realtime Database — one `/state` node, sole source of truth
- **Auth:** one hidden email/password account; DB rules require `auth != null`
- **Hosting:** GitHub Pages, served from `main` at the repo root
- **Install:** add-to-home-screen on iOS (`manifest.webmanifest` + `apple-touch-icon.png`)

## Buttons beyond "done"

- **pour a different one** — swap today's task; resets overnight.
- **can't do this one — hide it** — permanently removes that task from your
  rotation (stored in Firebase; only "reset everything" brings it back) and logs
  it for a later pool cleanup.
- **skip today** (above the tabs) — skips the whole day: doesn't advance your
  clean-week streak and doesn't reset it. Once per day, no undo.
- **stayed in — didn't talk to anyone today** (talk only) — the day still counts
  as clean if Move and Tidy are done; talk gets no tally mark but the streak
  isn't broken.
- **did something else instead** (tidy only) — logs the day as a skip.

## Configuring Firebase

Edit the `firebaseConfig` block near the top of the `<script>` in `index.html`,
plus `AUTH_EMAIL` / `AUTH_PASSWORD`. Get these from the Firebase console:

- Config object: **Project settings → Your apps → Web app**
- Credentials: the user you created under **Authentication → Users**

Database rules (Realtime Database → Rules):

```json
{
  "rules": {
    "state": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

> The config and the sign-in password ship in the page source (GitHub Pages
> serves them publicly regardless of repo visibility). The DB is only as
> protected as that password — don't reuse it anywhere else.

## CSV export

The **export new activity (CSV)** button downloads everything recorded *since the
last export* — columns `date,category,status,task`, where `status` is one of
`done`, `skip` (tidy "something else instead"), `excused` (talk "stayed in"),
`skip_day`, or `irrelevant` (with the hidden task named in the `task` column). It
advances the `lastExportDate` marker in the Firebase state on success.

## Icons

`icon-192.png`, `icon-512.png`, `apple-touch-icon.png` are placeholder glyphs
(brass droplet on the chalkboard ground). Regenerate or replace anytime;
`scripts/gen_icons.py` produces them with the Python standard library only.
