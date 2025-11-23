# Deployment Instructions for Camer-Eat Project (Without Docker)

This guide explains how to deploy the Camer-Eat project manually without Docker, including setup for Django backend, Next.js frontend, and nginx configuration.

---

## 1. Prepare the Server

- Make sure you have the following installed on the server:
  - Python 3.10+ (or compatible version)
  - Node.js 18+ and npm or pnpm
  - MySQL Server (or access to the MySQL database)
  - nginx
  - virtualenv

---

## 2. Django Backend Setup

1. **Navigate to the backend directory:**

```bash
cd /home/migos/Bureau/GTchemou/camereatmain/livraison_nourriture
```

2. **Create a Python virtual environment and activate it:**

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install Python dependencies:**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Set environment variables (adapt as needed):**

```bash
export DJANGO_SETTINGS_MODULE=backend.settings
export DB_NAME=your_db_name
export DB_USER=your_db_user
export DB_PASSWORD=your_db_password
export DB_HOST=your_db_host
export DB_PORT=3306
```

5. **Apply database migrations:**

```bash
python manage.py migrate
```

6. **Collect static files:**

```bash
python manage.py collectstatic --noinput
```

7. **Create a superuser (if needed):**

```bash
python manage.py createsuperuser
```

8. **Run Gunicorn to serve the Django app:**

```bash
gunicorn backend.wsgi:application --bind 127.0.0.1:8000 --workers 4 --threads 2
```

You may want to run this command inside a process manager like `systemd` or `supervisor` for production.

---

## 3. Next.js Frontend Setup

1. **Navigate to the project root directory:**

```bash
cd /home/migos/Bureau/GTchemou/camereatmain
```

2. **Install Node.js dependencies:**

```bash
npm install
```

Alternatively use `pnpm install` if you use pnpm.

3. **Build the Next.js app:**

```bash
npm run build
```

4. **Start the Next.js server:**

```bash
npm start
```

By default, this runs the Next.js app on port 3000.

---

## 4. Nginx Configuration

- Replace the existing nginx configuration with the provided `nginx.conf` file configured to:

  - Proxy `/` to Next.js on `localhost:3000`
  - Proxy `/api` to Django backend on `localhost:8000`
  - Serve Django static files from `/home/migos/Bureau/GTchemou/camereatmain/livraison_nourriture/staticfiles/`

- Place the `nginx.conf` file in `/etc/nginx/sites-available/camer-eat` (or appropriate location).

- Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/camer-eat /etc/nginx/sites-enabled/
```

- Test nginx configuration:

```bash
sudo nginx -t
```

- Reload nginx:

```bash
sudo systemctl reload nginx
```

---

## 5. Firewall Configuration (optional but recommended)

Allow HTTP (80) and HTTPS (443):

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw reload
```

---

## 6. Running the Application

- Make sure Gunicorn and Next.js are running in the background or managed by a process manager.
- Nginx will handle SSL termination and proxy requests to your backend and frontend.

---

## Notes

- Media files are hosted on Cloudinary, so no need to serve media files via nginx.
- Adjust environment variables according to your production database and secrets.
- Consider using `pm2` or `systemd` for managing the Next.js server.
- For production, set `DEBUG = False` in Django settings and add your domain to `ALLOWED_HOSTS`.

---

This completes the manual deployment setup for the Camer-Eat project without Docker.
