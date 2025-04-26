# django-bootstrap

- Quick setup of django with drf

To Clone:
git clone https://github.com/pystrap/django-bootstrap.git my-project
cd my-project
remove current repo file (.git) on explorer
rmdir /s /q .git (if using git bash do rm -rf .git, Powershell: Remove-Item -Recurse -Force .git)

Create venv:
Go to Settings on Pycharm
select Project: <project-name>
Select Python Interpreter
Add interpreter next to the python interpreter selector
Click Add Local Interpreter
On the virtual environment tab click new and set it up

- move .env to venv directory
  configure .env including db connection details
- create /media
- move cors_server.py to /media for serving media storage files --
- to start media files server:
  cd media

- install dependencies
  pip install -r requirements.txt

  Start Server
  python manage.py runserver
  python cors_server.py 8888

- (or any port for media)

  Initialize new repo:
  git init
  git remote add origin https://github.com/your-username/my-new-project.git
  git add .
  git commit -m "Initial commit from my Django bootstrap"
  git push -u origin main

If you need to login, Install github CLI if not already install, then:
gh auth login
use ssh accept login in browser and add projects/organizations
