# OSIRIS integration bundle

This folder is reserved for the OSIRIS application source and resources.

## Source
- Upstream: https://github.com/simplifaisoul/osiris
- License: MIT (retain the upstream LICENSE and notices)
- Architecture: Next.js 16, React 19, TypeScript, MapLibre GL

## Import the complete source on Windows

Run `IMPORT_OSIRIS.ps1` from the repository root. It clones the upstream repository into a temporary directory and copies the application source, public assets, engine, intel service, tools, docs, and required project configuration into `globe/osiris/`.

It deliberately excludes `.git`, `.env`, `node_modules`, Python virtual environments, caches, runtime logs, and generated build output.

After import:

```powershell
cd globe/osiris
npm install
npm run dev
```

Open http://localhost:3000.

GitHub Pages cannot execute the Next.js API routes or server runtime. Deploy the OSIRIS app separately (for example, on a Node-capable host) and point the Nexus Radar globe launcher at that deployment when ready.

## Visual theme
The initial `globe.html` launcher uses a bright interface. The upstream app's visual system is kept intact in the imported source so the light-theme conversion can be done as a separate, reviewable change.

## License notes
OSIRIS is MIT-licensed. Keep its LICENSE file and copyright notice with the imported source. Nexus Radar is separately licensed under GPL-3.0; preserve both license notices when distributing the combined project.
