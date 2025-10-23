# GitHub Pages Setup Guide

## ✅ Files Prepared

The following files have been created to support GitHub Pages deployment:

1. **`docs/.nojekyll`** - Prevents Jekyll processing (ensures files with underscores and special names work correctly)
2. **`docs/index.html`** - Redirect page that forwards to `methodology/index.html`
3. **`docs/methodology/README.md`** - Comprehensive documentation for the methodology

## 🚀 Deployment Steps

### 1. Enable GitHub Pages

1. Go to your GitHub repository settings
2. Navigate to **Pages** (in the left sidebar under "Code and automation")
3. Under **Source**, select:
   - **Source:** Deploy from a branch
   - **Branch:** `main` (or your default branch)
   - **Folder:** `/docs`
4. Click **Save**

### 2. Wait for Deployment

GitHub will automatically build and deploy your site. This typically takes 1-2 minutes.

You'll see a message like:
```
Your site is live at https://cprima.github.io/micro-casting-prototype/
```

### 3. Access Your Methodology

- **Direct URL:** `https://cprima.github.io/micro-casting-prototype/methodology/`
- **Root URL:** `https://cprima.github.io/micro-casting-prototype/` (redirects to methodology)

## 📁 Directory Structure

```
docs/
├── .nojekyll                    # Disables Jekyll processing
├── index.html                    # Redirects to methodology
├── methodology/
│   ├── index.html               # Main methodology interface
│   ├── data.json                # Methodology data (v0.3.2)
│   ├── README.md                # Documentation
│   ├── schema-v0.3.0-proposal.yaml
│   ├── schema-gate-predicates.yaml
│   ├── tag-canonicalization.yaml
│   └── screenshots/
├── skills/                      # Other docs
├── modelcontextprotocol.io/     # Other docs
└── ...
```

## ✅ Verification Checklist

- [x] `.nojekyll` file created in `docs/`
- [x] `docs/index.html` redirects to methodology
- [x] All file paths in `methodology/index.html` are relative
- [x] `data.json` is in same directory as `index.html`
- [x] README.md created with comprehensive documentation
- [x] Solarized Light theme applied
- [x] Version updated to v0.3.2

## 🎨 Features

The deployed methodology includes:

- **Interactive Progress Tracking** - LocalStorage persists completed nodes
- **Filtering & Search** - Filter by level, door type, search by text
- **Evidence Requirements** - Clear indication of what evidence is needed when
- **Dependency Visualization** - Shows blocking relationships with reasons
- **Solarized Light Theme** - Comfortable reading experience
- **Comprehensive Footer** - Reference documentation for all concepts
- **Mobile Responsive** - Works on all screen sizes

## 🔧 Troubleshooting

### Site Not Loading

If the site doesn't load after enabling Pages:

1. Check GitHub Actions tab for deployment status
2. Verify branch and folder settings are correct
3. Ensure `.nojekyll` file exists
4. Clear browser cache and try again

### 404 Errors

If you get 404 errors:

1. Verify files are committed and pushed to GitHub
2. Check file paths are relative (not absolute)
3. Ensure `data.json` is in `docs/methodology/` directory
4. Verify repository is public (or you have GitHub Pro for private pages)

### JavaScript Not Working

If the methodology loads but doesn't function:

1. Check browser console for errors
2. Verify `data.json` is accessible
3. Try clearing localStorage: `localStorage.clear()`
4. Check CORS settings (usually not an issue with GitHub Pages)

## 📝 Next Steps

After deployment, you can:

1. **Test the live site** - Visit your GitHub Pages URL
2. **Share the link** - Others can now use your methodology
3. **Track progress** - Progress is saved per browser via localStorage
4. **Update content** - Edit `data.json` and push to update

## 🎯 Custom Domain (Optional)

To use a custom domain:

1. Add a `CNAME` file to `docs/` with your domain
2. Configure DNS at your domain provider
3. Update GitHub Pages settings with custom domain

## 📊 Analytics (Optional)

To add analytics:

1. Add Google Analytics or Plausible script to `index.html`
2. Track page views, interactions, progress completion rates

---

**Ready to deploy!** Just push these changes to GitHub and enable Pages in repository settings.
