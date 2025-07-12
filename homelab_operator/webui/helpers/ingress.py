import os
import subprocess
from django.template.loader import render_to_string
from ..models import Ingress

def reload_nginx():
    # Reload nginx (in production you'd want proper error handling)
    # TODO error handling
    # TODO rollback on error
    # TODO log in AppState
    # TODO test (new config(s)) before reloading
    try:
        subprocess.run(['nginx', '-s', 'reload'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        # TODO log in AppState
        raise Exception(f"Failed to reload nginx: {e}")

def generate_ingress_nginx_config(ingress):
    """Generate nginx configuration with ingress rules."""

    # Get all Ingresses for same hostname
    ingresses = Ingress.objects.filter(enabled=True, hostname=ingress.hostname).order_by('priority')

    # Generate nginx config
    config_content = render_to_string('nginx/ingress.conf', {
        'hostname': ingress.hostname,
        'ingresses': ingresses,
    })

    # Write to nginx config file
    config_path = f'/app/nginx/nginx_ingress_{ingress.hostname}.conf'  # TODO variable path?
    if os.getenv('DEBUG', False):
        print('Using DEUBG')  # TODO remove
        config_path = f'/home/franz/main/project/homelab-operator/nginx/nginx_ingress_{ingress.hostname}.conf'
    with open(config_path, 'w') as f:
        f.write(config_content)

    reload_nginx()

def delete_ingress_nginx_conf(ingress):
    ...
