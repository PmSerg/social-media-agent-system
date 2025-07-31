# GitHub Repository Setup Instructions

Follow these steps to push your Social Media Agent System to GitHub:

## 1. Create a New GitHub Repository

1. Go to [GitHub.com](https://github.com) and sign in
2. Click the **"+"** icon in the top right → **"New repository"**
3. Configure your repository:
   - **Repository name**: `social-media-agent-system` (or your preferred name)
   - **Description**: "Production-ready multi-agent system for automated social media content creation"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

## 2. Push Your Local Repository to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/social-media-agent-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

If you're using SSH instead of HTTPS:
```bash
git remote add origin git@github.com:YOUR_USERNAME/social-media-agent-system.git
git push -u origin main
```

## 3. Set Up Repository Secrets

Go to your repository on GitHub → Settings → Secrets and variables → Actions

Add these secrets for GitHub Actions to work:
- `OPENAI_API_KEY`: Your OpenAI API key
- `NOTION_TOKEN`: Your Notion integration token
- `NOTION_DATABASE_ID`: Your Notion database ID
- `SERPAPI_KEY`: Your SerpAPI key

## 4. Configure Branch Protection (Optional but Recommended)

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging

## 5. Enable GitHub Actions

1. Go to the Actions tab in your repository
2. You should see the workflows we created
3. They will run automatically on push/PR

## 6. Add Repository Topics

Go to the main repository page → ⚙️ (gear icon) next to About

Add topics:
- `python`
- `fastapi`
- `agency-swarm`
- `ai-agents`
- `social-media`
- `automation`
- `gpt-4`
- `notion-api`

## 7. Update Repository Settings

### General Settings:
- ✅ Issues
- ✅ Preserve this repository
- ✅ Discussions (optional)
- ❌ Sponsorships (unless you want them)

### Features:
- ✅ Wikis (for documentation)
- ✅ Projects (for task management)

## 8. Create Initial GitHub Issues (Optional)

Consider creating these issues to track future work:
1. "Add authentication system"
2. "Implement rate limiting dashboard"
3. "Add support for more social platforms"
4. "Create admin interface"
5. "Add analytics and reporting"

## 9. Set Up GitHub Pages (Optional)

To host documentation:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /docs (create docs folder first)

## Quick Commands Reference

```bash
# Check current remotes
git remote -v

# Change remote URL if needed
git remote set-url origin NEW_URL

# Push all branches
git push --all origin

# Push all tags
git push --tags origin

# Create and push a new branch
git checkout -b feature/new-feature
git push -u origin feature/new-feature
```

## Troubleshooting

### Authentication Issues
If you get authentication errors:
1. Use a Personal Access Token instead of password
2. Go to GitHub → Settings → Developer settings → Personal access tokens
3. Generate new token with `repo` scope
4. Use token as password when pushing

### Large Files
If you have large files:
```bash
# Install Git LFS
git lfs track "*.pkl"
git lfs track "*.model"
git add .gitattributes
git commit -m "Add Git LFS tracking"
```

## Next Steps

After pushing to GitHub:
1. Add a nice repository banner/logo
2. Create a detailed Wiki
3. Set up project boards for task management
4. Configure webhooks for deployment
5. Add badges to README (build status, coverage, etc.)

---

🎉 **Congratulations!** Your Social Media Agent System is now on GitHub!