# Structure of the NGINX services
The structure might be a bit unintuitive. I chose it to be as reliable as possible.

```
nginx.conf (Started from Dockerfile) (pid1)
├─ server_name localhost -> nginx/homelab-operator.conf
├─ server_name _ -> nginx/ingress-forward.conf (Forwarding to second nginx instance on localhost:90)

ingress.conf (pid2)
├─ server_name _ -> nginx/ingress.conf
```
