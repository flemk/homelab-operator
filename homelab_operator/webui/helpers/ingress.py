import os
import subprocess
from django.template.loader import render_to_string
from ..models import Ingress, AppState

def test_nginx_ingress_config():
    """Test the nginx configuration for syntax errors."""
    # Run nginx -t to test the configuration
    if os.getenv('DEBUG', False):
        print("Skipping nginx config test in DEBUG mode")
        return True

    result = subprocess.run(['nginx', '-t', '-c', '/app/nginx/ingress-handler.conf'],
                            capture_output=True, text=True)

    if result.returncode != 0:
        return False

    return result.stdout.strip()

def reload_nginx_ingress():
    # Reload nginx (in production you'd want proper error handling)
    # TODO rollback on error
    if os.getenv('DEBUG', False):
        print("Skipping nginx reload in DEBUG mode")
        return True

    app_state = AppState.objects.first()

    # Get nginx PID from file and send HUP signal to reload
    pid_file = '/var/run/nginx_ingress.pid'

    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            pid = f.read().strip()
        try:
            subprocess.run(['kill', '-HUP', pid], check=True)
            return True
        except Exception as e:
            app_state.add_exception(f"Failed to reload nginx: {e}")
            return False
    else:
        raise FileNotFoundError(f"Nginx PID file {pid_file} does not exist.")

def generate_ingress_nginx_config(ingress, delete=False):
    """Generate nginx configuration with ingress rules."""

    # Get all Ingresses for same hostname
    ingresses = Ingress.objects.filter(enabled=True, hostname=ingress.hostname).order_by('priority')

    if delete:
        # Remove the specific ingress from the list
        ingresses = ingresses.exclude(id=ingress.id)

    if not ingresses:
        # If no ingresses left, remove the config file
        config_path = f'/app/nginx/nginx_ingress_{ingress.hostname}.conf'
        if os.getenv('DEBUG', False):
            print("Skipping nginx config generation in DEBUG mode")
            config_path = f'/home/franz/main/project/homelab-operator/nginx/nginx_ingress_{ingress.hostname}.conf'  # TODO

        if os.path.exists(config_path):
            os.remove(config_path)
        return

    # Generate nginx config
    config_content = render_to_string('nginx/ingress.conf', {
        'hostname': ingress.hostname,
        'ingresses': ingresses,
    })

    # Write to nginx config file
    config_path = f'/app/nginx/nginx_ingress_{ingress.hostname}.conf'
    if os.getenv('DEBUG', False):
        print("Using debug path for nginx config in DEBUG mode")
        config_path = f'/home/franz/main/project/homelab-operator/nginx/nginx_ingress_{ingress.hostname}.conf'  # TODO

    with open(config_path, 'w') as f:
        f.write(config_content)

    if test_nginx_ingress_config() is False:
        if os.path.exists(config_path):
            os.remove(config_path)
        raise RuntimeError("Nginx configuration test failed. Please check the syntax.")

    reload_nginx_ingress()
