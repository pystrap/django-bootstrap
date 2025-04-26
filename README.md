# Django Bootstrap

🚀 Quick setup for Django with Django REST Framework (DRF).

---

## 📥 To Clone:

```bash
git clone https://github.com/pystrap/django-bootstrap.git my-project
cd my-project
```

Remove the current Git history:

- **File Explorer:** Delete the `.git` folder manually (make sure hidden files are visible)
- **Git Bash:**
  ```bash
  rm -rf .git
  ```
- **Command Prompt:**
  ```cmd
  rmdir /s /q .git
  ```
- **PowerShell:**
  ```powershell
  Remove-Item -Recurse -Force .git
  ```

---

## 🛠️ Open Project and Create a Virtual Environment:

In **PyCharm**:

- Open folder (project)

1. Go to **Settings** → **Project: _your-project-name_** → **Python Interpreter**
2. Click the ⚙️ next to the interpreter selector → **Add Interpreter**
3. Choose **Add Local Interpreter**
4. Under the **Virtual Environment** tab, click **New environment** and set it up.

Or manually via terminal:

```bash
python -m venv venv
source venv/Scripts/activate  # (on Windows)
```

---

## ⚙️ Initial Setup:

- Move the `.env` file into your `venv/` directory.
- Configure your `.env` (especially database connection details).
- Create a `/media/` folder for serving uploaded files.
- Move `cors_server.py` to the media folder created.

To serve media files:

```bash
cd media
python cors_server.py 8888  # or any port
```

---

## 📦 Install Dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔥 Setup Database:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🚀 Start Servers:

- Start Django development server:

  ```bash
  python manage.py runserver
  ```

- Start Media server:

  ```bash
  cd media
  python cors_server.py 8888
  ```

_(Use any free port if 8888 is busy.)_

---

## 🌐 Initialize a New Git Repository:

```bash
git init
git remote add origin https://github.com/your-username/my-new-project.git
git add .
git commit -m "Initial commit from my Django bootstrap"
git push -u origin main
```

---

## 🔐 GitHub Authentication (Optional):

If you need to authenticate with GitHub:

1. Install the [GitHub CLI](https://cli.github.com/) if not already installed.
2. Run:

   ```bash
   gh auth login
   ```

3. Use **SSH** method → Accept login in browser → Add your project to your GitHub account or organization.

---

## 📚 Notes:

- `cors_server.py` is a lightweight server for media file handling in development.

---

# 🎉 Happy Building!
