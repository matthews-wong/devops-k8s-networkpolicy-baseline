# devops-k8s-networkpolicy-baseline

A small default-deny NetworkPolicy baseline for a two-tier app (`web` -> `api`)
in its own namespace. Everything is plain YAML; nothing talks to anything until a
policy says it can.

## Layout

| File | Purpose |
| --- | --- |
| `manifests/00-namespace.yaml` | `shop` namespace with Pod Security `restricted` enforced |
| `manifests/10-default-deny.yaml` | Deny all ingress and egress for every pod in the namespace |
| `manifests/20-allow-dns.yaml` | Let pods resolve names through CoreDNS in `kube-system` |
| `manifests/30-api.yaml` | `api` Deployment + Service |
| `manifests/31-web.yaml` | `web` Deployment + Service |
| `manifests/40-allow-web-to-api.yaml` | Explicit `web` -> `api` egress/ingress pair |
| `manifests/41-allow-ingress-to-web.yaml` | Ingress controller -> `web` only |
| `scripts/check-selectors.py` | Fails if a policy selects no workload |

## Design notes

- Default deny covers both directions, so each allowed flow needs a matching
  egress rule on the client and ingress rule on the server.
- DNS is the first thing that breaks under default deny; it is allowed on UDP and
  TCP 53 to the CoreDNS pods only, not to the whole of `kube-system`.
- Namespaces are matched with the immutable `kubernetes.io/metadata.name` label.
- NetworkPolicy is only enforced if the CNI supports it (Calico, Cilium, ...).

## Validate

```sh
make validate
```

Runs `kubeconform -strict` against Kubernetes 1.31 and the selector check.
Neither needs a cluster, so this does not prove a CNI enforces the policies.

## Caveats

- `api` and `web` both run `nginx-unprivileged` as stand-ins so the manifests are
  realistic (non-root, read-only root filesystem) without needing a custom image.
- The image is pinned by tag, not digest; pin a digest before using this for real.
