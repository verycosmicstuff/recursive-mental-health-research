---
description: commit and push latest changes to GitHub
---

# How to Push Updates to GitHub

This workflow covers how to keep your GitHub repo up to date after working on the project.

## Steps

1. Open **GitHub Desktop**

2. You will see a list of changed files in the left panel. Review them to make sure you're only committing code files (`.py`, `.html`, `.bat`, `.md`) and not any data files (`results.tsv`, `app.log`, `experiments/`). The `.gitignore` handles this automatically.

3. In the **Summary** box (bottom left), write a short description of what you changed. Examples:
   - `Add hardware monitor tab to dashboard`
   - `Fix pause/resume bug in main loop`
   - `Improve scoring weights in config`

4. Click **"Commit to main"**

5. Click **"Push origin"** (top right blue button)

Your changes are now live on GitHub!

## When to Push

Good times to push:
- After fixing a bug
- After adding a new feature or tab to the dashboard
- When you have a notable new best_strategy result you want to share
- At the end of a research run when you want to snapshot the code state

## What NOT to Push

The `.gitignore` already blocks these, but double-check:
- Never manually add `results.tsv` to a commit (it contains all your raw run data)  
- Never add the `experiments/` folder (thousands of JSON files, not useful to others)
- Never add `app.log` or `*.backup` files
