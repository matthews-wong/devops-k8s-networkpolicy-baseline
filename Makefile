K8S_VERSION ?= 1.31.0

.PHONY: validate
validate:
	kubeconform -strict -summary -kubernetes-version $(K8S_VERSION) manifests
	python3 scripts/check-selectors.py
