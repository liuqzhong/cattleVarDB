#!/bin/bash
# ============================================
# Clean Git History and Push
# 清理 Git 历史并推送
# ============================================

echo "Step 1: Creating a clean orphan branch..."
git checkout --orphan clean_branch

echo "Step 2: Adding all files (respecting .gitignore)..."
git add -A

echo "Step 3: Creating initial commit..."
git commit -m "Initial commit: Cattle SNP Effect Value Database

This is a fresh start after removing large data files from git history.

Features:
- FastAPI backend with PostgreSQL database
- Vue 3 frontend with TypeScript
- 47 SNP records with 578 targets
- 27,166 effect value records
- RESTful API with pagination and search
- Docker support for easy deployment

Changes:
- Fixed database schema (lowercase table names)
- Fixed SQLAlchemy 2.0 compatibility
- Added database initialization scripts
- Removed large data files from git tracking
"

echo "Step 4: Deleting master branch..."
git branch -D master

echo "Step 5: Renaming clean_branch to master..."
git branch -m master

echo "Step 6: Force pushing to GitHub..."
git push -u origin master --force

echo "Done! Your code is now on GitHub."
