# Deploy KKEF on PythonAnywhere

## 1. Push code to GitHub (local machine)

```powershell
cd C:\Users\pc\KKEF
git init
git add .
git commit -m "Initial KKEF platform"
git branch -M main
git remote add origin https://github.com/Drmartoh/kkef.git
git push -u origin main
```

## 2. Clone on PythonAnywhere

Open **Bash** on [PythonAnywhere](https://www.pythonanywhere.com/) and run:

```bash
export PA_USER=your_pythonanywhere_username
bash /home/$PA_USER/kkef/deploy/pythonanywhere/setup.sh
```

If the repo is not cloned yet:

```bash
git clone https://github.com/Drmartoh/kkef.git ~/kkef
export PA_USER=$(whoami)
bash ~/kkef/deploy/pythonanywhere/setup.sh
```

## 3. Web app configuration

| Setting | Value |
|--------|--------|
| Source code | `/home/<user>/kkef` |
| Working directory | `/home/<user>/kkef` |
| Virtualenv | `/home/<user>/kkef/venv` |
| WSGI file | `/home/<user>/kkef/deploy/pythonanywhere/wsgi.py` |

**Static files mapping:** URL `/static/` → directory `/home/<user>/kkef/staticfiles`

**Media files mapping:** URL `/media/` → directory `/home/<user>/kkef/media`

Edit `deploy/pythonanywhere/wsgi.py` and set `PA_USERNAME` to your PythonAnywhere username (or export `PA_USERNAME` in the Web tab environment).

Set a strong `DJANGO_SECRET_KEY` in `.env`, then click **Reload**.

## Notes

- **Free tier:** SQLite + in-memory Channels (no WebSockets). Real-time notifications need a paid plan + Redis.
- **Demo login:** see root `README.md` (`seed_demo`).
