# GitHub Student Branch & Submission Guide

## AI-Powered Insider Threat Detection and Behavioral Security Intelligence Platform

**Project Repository URL:**
`https://github.com/springboardmentor150-png/AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform`

---

## 📌 Submission Instructions for Students

Every student works on the complete project from beginning to end on their individual workspace branch.

### Step 1 — Accept the GitHub Invitation
1. Sign in to your GitHub account.
2. Open the email / repository invitation link sent by your mentor and click **Accept invitation**.
3. Confirm you can view the repository without errors.

### Step 2 — Clone the Repository
Open Git Bash or Command Prompt:
```bash
git clone https://github.com/springboardmentor150-png/AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform.git
cd AI-Powered-Insider-Threat-Detection-and-Behavioral-Security-Intelligence-Platform
```

### Step 3 — Create Your Own Student Branch
Create and switch to your designated branch:
```bash
git checkout -b student-yourname
```
*Example:* `git checkout -b student-ananya`

### Step 4 — Check Your Active Branch
```bash
git branch
```
Ensure your branch is marked with an asterisk `*`.

### Step 5 — Verify Your Project Code
Ensure all files from the `itbis/` directory (`backend/`, `frontend/`, `scripts/`, `README.md`) are present.
Run the automated test suite to confirm everything is passing:
```bash
cd backend
python -m pytest tests/test_api.py -v
```

### Step 6 — Commit Your Work
```bash
git status
git add .
git commit -m "Complete AI-Powered Insider Threat Detection platform with ML models and full stack SOC UI"
```

### Step 7 — Push Your Branch to GitHub
```bash
git push -u origin student-yourname
```

### Step 8 — Create a Pull Request (PR)
1. Open the repository on GitHub.
2. Go to **Pull requests** &rarr; **New pull request**.
3. Select `main` as the base branch and `student-yourname` as the compare branch.
4. Set Title: `Complete Project Submission - Your Name`
5. Click **Create pull request**.

### Step 9 — Mentor Review
- Wait for mentor review and feedback.
- If changes are requested, apply them on the same branch, commit, and push.