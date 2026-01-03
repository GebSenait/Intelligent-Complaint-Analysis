# Quick Reference: CMD Commands for This Project

## Navigate to Project Directory

First, always navigate to your project directory:

```cmd
cd "D:\Senait Doc\KAIM 8 Doc\Intelligent-Complaint-Analysis"
```

---

## Git Commands

### Check Git Installation
```cmd
git --version
```
**Expected output:** `git version 2.52.0.windows.1` (or similar)

### Check Current Branch
```cmd
git branch
```
**Expected output:** Shows `* task-1-eda-preprocessing` (asterisk indicates current branch)

### Check All Branches
```cmd
git branch -a
```
**Expected output:** Shows `main` and `task-1-eda-preprocessing`

### Check Git Status
```cmd
git status
```
**Expected output:** Shows current branch and untracked files

### View Git Log (if you have commits)
```cmd
git log --oneline
```

---

## Virtual Environment Commands

### Activate Virtual Environment
```cmd
venv\Scripts\activate.bat
```
**Note:** After activation, you'll see `(venv)` at the start of your command prompt

### Deactivate Virtual Environment
```cmd
deactivate
```

### Check Python Version (in venv)
```cmd
venv\Scripts\python.exe --version
```
**Expected output:** `Python 3.12.0`

---

## Dependency Check Commands

### List All Installed Packages
```cmd
venv\Scripts\python.exe -m pip list
```

### Check Specific Packages from requirements.txt
```cmd
venv\Scripts\python.exe -m pip list | findstr "pandas numpy matplotlib seaborn jupyter notebook"
```

### Check Package Versions
```cmd
venv\Scripts\python.exe -m pip show pandas
venv\Scripts\python.exe -m pip show numpy
venv\Scripts\python.exe -m pip show matplotlib
```

### Verify All Requirements Are Installed
```cmd
venv\Scripts\python.exe -m pip check
```

---

## Quick Verification Checklist

Run these commands in sequence to verify everything is set up:

```cmd
REM 1. Navigate to project
cd "D:\Senait Doc\KAIM 8 Doc\Intelligent-Complaint-Analysis"

REM 2. Check git
git --version
git branch
git status

REM 3. Check Python in venv
venv\Scripts\python.exe --version

REM 4. Check key dependencies
venv\Scripts\python.exe -m pip show pandas
venv\Scripts\python.exe -m pip show numpy
venv\Scripts\python.exe -m pip show matplotlib
venv\Scripts\python.exe -m pip show jupyter
```

---

## Troubleshooting

### If Git Commands Don't Work in CMD:

1. **Check if Git is in PATH:**
   ```cmd
   where git
   ```
   If this returns nothing, Git might not be in your system PATH.

2. **Try using full path to Git:**
   - Git is usually installed at: `C:\Program Files\Git\cmd\git.exe`
   - Or: `C:\Program Files (x86)\Git\cmd\git.exe`
   
   You can add it to PATH or use the full path:
   ```cmd
   "C:\Program Files\Git\cmd\git.exe" --version
   ```

3. **Restart CMD after installing Git** (if you just installed it)

### If Python Commands Don't Work:

1. **Make sure you're using the venv Python:**
   ```cmd
   venv\Scripts\python.exe --version
   ```

2. **If venv doesn't exist, recreate it:**
   ```cmd
   py -m venv venv
   ```

---

## Expected Results

### Git Status Should Show:
```
On branch task-1-eda-preprocessing

No commits yet

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	README.md
	data/
	docs/
	notebooks/
	requirements.txt
	venv/
```

### Key Packages Should Show:
- pandas: 2.3.3
- numpy: 2.4.0
- matplotlib: 3.10.8
- seaborn: 0.13.2
- jupyter: 1.1.1
- notebook: 7.5.1
- ipykernel: 7.1.0

---

## Launch Jupyter Notebook

Once everything is verified:

```cmd
REM Activate venv first
venv\Scripts\activate.bat

REM Launch Jupyter
jupyter notebook
```

Or directly:
```cmd
venv\Scripts\jupyter.exe notebook
```

