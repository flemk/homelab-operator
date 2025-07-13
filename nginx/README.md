# Structure of the NGINX services
The structure might be a bit unintuitive. I chose it to be as reliable as possible.

`nginx.conf` only serves homelab-operator and `ingress-forward.conf` only handles requests which don't have homelab-operator as target. It is only used for ingresses.

So when the ingress configs somehow get messed up, homelab operator should still be accessible.

```
nginx.conf (Started from Dockerfile) (pid1)
├─ server_name localhost -> nginx/homelab-operator.conf
├─ server_name _ -> nginx/ingress-forward.conf (Forwarding to second nginx instance on localhost:90)

ingress-forward.conf (pid2)
├─ server_name _ -> nginx/ingress.conf
```
