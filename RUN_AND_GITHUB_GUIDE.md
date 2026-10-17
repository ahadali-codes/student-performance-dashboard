# Run the project and push it to GitHub

## 1. Install the tools
Install Python 3.11 or 3.12, Git and VS Code. On Windows, select “Add Python to PATH” during Python installation. Restart the terminal after installing tools.

Confirm:
```bash
python --version
git --version
```
On Windows, `py --version` may work if `python` does not. On macOS/Linux, use `python3` if needed.

## 2. Open the correct folder
Extract the ZIP. In VS Code choose File → Open Folder and open `student-academic-dashboard`, the folder directly containing `app.py`, `requirements.txt` and `src/`.
Choose Terminal → New Terminal. These commands also work in another editor's terminal or a standalone terminal opened in the same folder.

## 3. Create a virtual environment
```bash
python -m venv .venv
```
Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```
macOS/Linux:
```bash
source .venv/bin/activate
```
In VS Code install Microsoft's Python extension, run “Python: Select Interpreter” from the command palette and choose `.venv`.

## 4. Install dependencies and run
```bash
pip install -r requirements.txt
streamlit run app.py
```
Open the Local URL printed by Streamlit, usually http://localhost:8501. The terminal must stay open. Stop with Ctrl+C.

If activation is blocked on Windows, use these commands directly; no execution-policy change is required:
```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```
Equivalent on macOS/Linux:
```bash
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```
If `streamlit` is not recognized after activation, run `python -m streamlit run app.py`.
If port 8501 is occupied, use `python -m streamlit run app.py --server.port 8502`.

## 5. Explore and test
The app starts with bundled fictional data. Use sidebar navigation, change filters, view the cleaning audit and download a filtered CSV. Upload a CSV with the same 18 columns to analyze a different dataset. Remove the upload to restore the demo.

Run the regression suite:
```bash
python -m unittest discover -s tests -v
```
The `src/` modules explain where data cleaning, scoring and plots live. Read these before presenting the project. Do not double-click `app.py` or run it with the ordinary Python Run button; Streamlit needs its own launch command.

## 6. Make your first Git commit
Run inside the folder containing `app.py`:
```bash
git init
git add .
git commit -m "feat: build student academic performance dashboard"
git branch -M main
```
If Git asks for your identity, enter your own name and email, then repeat the commit:
```bash
git config user.name "Your Name"
git config user.email "your-email@example.com"
```
These commands set your identity for this repository only. `.gitignore` excludes virtual environments, caches and secrets.

## 7. Create the GitHub repository
Sign in to GitHub and create a repository named `student-academic-performance-dashboard`. Choose public if you want it visible in your portfolio. Create an **empty repository**: do not add a README, `.gitignore` or license on GitHub because your local project already has files.

Copy your repository's HTTPS URL. Replace `YOUR_USERNAME` below with your actual GitHub username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/student-academic-performance-dashboard.git
git push -u origin main
```
Complete the browser sign-in if prompted. GitHub account passwords are not used for HTTPS Git authentication; use the available Git credential manager/browser flow. Never put tokens in code, URLs or commits.

Refresh the GitHub repository page. You should see `app.py`, `src/`, `data/`, the notebook and README. The ZIP itself does not need to be uploaded.

If origin already exists:
```bash
git remote -v
```
If it points to the wrong repository, replace it intentionally:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/student-academic-performance-dashboard.git
```
If your remote already contains commits, do not force-push. Clone that repository into another folder, copy the extracted project files into it, review the changes, then commit and push.

## 8. Push future changes
After editing:
```bash
git status
git add .
git commit -m "docs: update dashboard documentation"
git push
```
Use a commit message matching your changes. VS Code's Source Control panel can stage, commit and push the same repository after setup. Terminal commands are generally easier to follow across editor versions.

## 9. Deploy on Streamlit Community Cloud
Go to https://share.streamlit.io/ and connect GitHub. Create an app and choose your repository, branch `main` and main file `app.py`. Choose Python 3.12 in Advanced settings and deploy. The platform returns your live application URL; add it to your GitHub About section and CV.

Official deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## 10. Finish the portfolio presentation
Run the app and capture genuine UI screenshots. Add them to the README screenshots section. Review `PROJECT_RESULTS.md`, explain the weights and risk rules in your own words and describe the synthetic-data limits. Add an appropriate license if you choose to distribute the project under one. No GitHub repository has been created, pushed or deployed on your behalf.
