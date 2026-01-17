@echo off
REM ============================================
REM Fresh Start - Clean Git History
REM 清理 Git 历史并重新推送
REM ============================================

echo.
echo WARNING: This will create a fresh git repository!
echo All commit history will be lost.
echo.
pause

REM Backup current git directory
echo.
echo Backing up current .git directory...
rename .git .git.backup

REM Initialize new repository
echo.
echo Initializing new git repository...
git init

REM Add all files
echo.
echo Adding files to git...
git add .

REM Create initial commit
echo.
echo Creating initial commit...
git commit -m "Initial commit: Cattle SNP Effect Value Database

This is a fresh start after removing large data files from git history.

Features:
- FastAPI backend with PostgreSQL database
- Vue 3 frontend with TypeScript
- 47 SNP records with 578 targets
- 27,166 effect value records
- RESTful API with pagination and search
- Docker support for easy deployment

Changes from previous version:
- Fixed database schema (lowercase table names)
- Fixed SQLAlchemy 2.0 compatibility
- Added database initialization scripts
- Removed large data files from git tracking
"

REM Add remote
echo.
echo Adding remote repository...
git remote add origin https://github.com/liuqzhong/cattleVarDB.git

REM Set branch name
git branch -M master

echo.
echo ============================================
echo Fresh repository created successfully!
echo ============================================
echo.
echo Now run: git push -u origin master --force
echo.
pause
