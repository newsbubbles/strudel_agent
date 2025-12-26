# Setup Instructions - Strudel Agent UI

## Phase 1 Complete! 🎉

The project structure has been scaffolded. Follow these steps to get the development server running.

---

## Step 1: Install Dependencies

```bash
cd ui
npm install
```

This will install:
- SvelteKit and Svelte 5
- TypeScript
- Tailwind CSS
- CodeMirror 6
- Utility libraries (clsx, tailwind-merge, tailwind-variants)

**Expected time**: 1-2 minutes

---

## Step 2: Initialize shadcn-svelte

```bash
npx shadcn-svelte@latest init
```

When prompted:
- **TypeScript**: Yes
- **Style**: Default
- **Base color**: Slate (or your preference)
- **Global CSS file**: `src/app.css`
- **Tailwind config**: `tailwind.config.js`
- **Import alias**: `$lib`

**Expected time**: 30 seconds

---

## Step 3: Install Required Components

```bash
# Install all components at once
npx shadcn-svelte@latest add carousel drawer button input textarea scroll-area separator badge
```

Or install individually:

```bash
npx shadcn-svelte@latest add carousel
npx shadcn-svelte@latest add drawer
npx shadcn-svelte@latest add button
npx shadcn-svelte@latest add input
npx shadcn-svelte@latest add textarea
npx shadcn-svelte@latest add scroll-area
npx shadcn-svelte@latest add separator
npx shadcn-svelte@latest add badge
```

**Expected time**: 1 minute

---

## Step 4: Start Development Server

```bash
npm run dev
```

The server will start at **http://localhost:5173**

You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Open http://localhost:5173 in your browser** - you should see the Phase 1 completion screen!

---

## Step 5: Verify Setup

### Check TypeScript

```bash
npm run check
```

Should output:
```
Loading svelte-check in workspace: ...
Getting Svelte diagnostics...
====================================

svelte-check found 0 errors and 0 warnings in X files
```

### Check Tailwind

Open http://localhost:5173 - the text should be styled with Tailwind classes.

### Check Strudel

Open browser console (F12) and type:

```javascript
typeof initStrudel
```

Should output: `"function"`

This confirms @strudel/web loaded successfully!

---

## Troubleshooting

### `npm install` fails

**Problem**: Dependency resolution errors

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

### shadcn-svelte init fails

**Problem**: Configuration conflicts

**Solution**: Manually create `components.json`:

```json
{
  "$schema": "https://shadcn-svelte.com/schema.json",
  "style": "default",
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/app.css",
    "baseColor": "slate"
  },
  "aliases": {
    "components": "$lib/components",
    "utils": "$lib/utils"
  }
}
```

Then retry component installation.

### Strudel not loading

**Problem**: CDN script blocked or slow

**Check**: Browser console for errors

**Solution**: 
1. Check internet connection
2. Try different CDN: `https://cdn.jsdelivr.net/npm/@strudel/web@latest`
3. Or download and host locally in `static/`

### Port 5173 already in use

**Problem**: Another process using port

**Solution**: Change port in `vite.config.ts`:

```typescript
server: {
  port: 5174, // Change to any available port
  // ...
}
```

### TypeScript errors after setup

**Problem**: Missing `.svelte-kit` folder

**Solution**:
```bash
npm run dev
```

This generates the `.svelte-kit` folder with type definitions.

---

## Next Steps

Once the dev server is running successfully:

1. ✅ **Phase 1 Complete**: Project scaffolded
2. ⏳ **Phase 2**: Implement type definitions (`src/lib/types/`)
3. ⏳ **Phase 3**: Build Svelte stores (`src/lib/stores/`)
4. ⏳ **Continue through phases** as outlined in `ui_implementation.md`

---

## Development Tips

### Hot Module Replacement (HMR)

SvelteKit has excellent HMR - changes to `.svelte` files update instantly without full page reload.

### TypeScript Checking

Run in watch mode during development:

```bash
npm run check:watch
```

### Code Formatting

```bash
npm run format
```

### Linting

```bash
npm run lint
```

---

## Project Structure Overview

After setup, your `ui/` folder should look like:

```
ui/
├── node_modules/              # Dependencies (gitignored)
├── src/
│   ├── lib/
│   │   ├── components/
│   │   │   └── ui/            # shadcn components (after install)
│   │   ├── utils/
│   │   │   └── cn.ts          # Tailwind class merger
│   │   ├── stores/            # (Phase 3)
│   │   ├── services/          # (Phase 4-6)
│   │   └── types/             # (Phase 2)
│   ├── routes/
│   │   ├── +layout.svelte     # Global layout
│   │   └── +page.svelte       # Home page
│   ├── app.html               # HTML template
│   └── app.css                # Global styles
├── static/                    # Static assets
├── .svelte-kit/               # Generated (gitignored)
├── package.json
├── svelte.config.js
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
├── components.json            # shadcn config (after init)
└── README.md
```

---

## Ready to Code!

You're all set! The foundation is in place and ready for Phase 2.

Happy coding! 🚀
