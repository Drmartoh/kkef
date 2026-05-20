#!/usr/bin/env bash
# Run from a PythonAnywhere Bash console after cloning the repo.
set -euo pipefail

PA_USER="${PA_USER:-$(whoami)}"
REPO_DIR="/home/${PA_USER}/kkef"

echo "==> Using home: /home/${PA_USER}"
cd "${REPO_DIR}"

if [[ ! -d .git ]]; then
  git clone https://github.com/Drmartoh/kkef.git "${REPO_DIR}"
  cd "${REPO_DIR}"
fi

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

if [[ ! -f .env ]]; then
  cp deploy/pythonanywhere/.env.example .env
  sed -i "s/<username>/${PA_USER}/g" .env
  sed -i "s/<YOUR_PA_USERNAME>/${PA_USER}/g" deploy/pythonanywhere/wsgi.py 2>/dev/null || true
  echo "Created .env — set DJANGO_SECRET_KEY before going live."
fi

export PA_USERNAME="${PA_USER}"
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_demo || true

echo ""
echo "Done. In the Web tab:"
echo "  - Virtualenv: /home/${PA_USER}/kkef/venv"
echo "  - WSGI file:  /home/${PA_USER}/kkef/deploy/pythonanywhere/wsgi.py"
echo "  - Static:     /home/${PA_USER}/kkef/staticfiles -> /static/"
echo "  - Media:      /home/${PA_USER}/kkef/media       -> /media/"
echo "Then Reload https://${PA_USER}.pythonanywhere.com"
