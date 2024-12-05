# Kubemize
Deploy Kubernetes Manifests and Helm Charts with one command

## About this project

---

### Why does this project exists?
I'm a very lazy person and don't want to execute dozens of commands to deploy a simple application which needs extra manifests or charts and I love to make
simple programs on my own to learn and get better in what I'm doing. The second thing is that I don't want to build CI/CD pipelines for simple applications or testing purposes. This project mainly helps me to learn Python a little bit more :D

I know that there are tools like kustomize and helmfile, but I'm still missing the ability to deploy manifests and charts with one tool AND using variables for templating. Lazy you know :D

### Warning
This project is in its early version and I don't know how often I'll update anything but I thought sharing this library to other lazy peoples as me :D

## Usage

---
#### Create Projects
Usage: `kubemize new [--project <dir>] [--config <path/to/config>]`

Examples:
```bash
# Create project in current directory
kubemize new

# Create project in specific directory
kubemize new --project /data/my-project

# Create project in specific directory and custom config file
kubemize new --project /data/my-project --config /data/my-project/stages/kubemize-dev.yaml
```

---
#### Plan Project
Usage: `kubemize plan [--project <dir>] [--config <path/to/config>] [--var "VAR_NAME=VAR_VALUE"] [--force]`

Examples:
```bash
# Plan project in current directory
kubemize plan
```

---
#### Apply Project
Usage: `kubemize apply [--project <dir>] [--config <path/to/config>] [--var "VAR_NAME=VAR_VALUE"] [--force]`

Examples:
```bash
# Apply project in current directory
kubemize apply
```

---
#### Destroy Project
Usage: `kubemize destroy [--project <dir>] [--config <path/to/config>] [--var "VAR_NAME=VAR_VALUE"] [--force]`

Examples:
```bash
# Destroy project in current directory
kubemize destroy
```

## Templating
This project uses the Jinja2 Template Engine for templating the helm values and manifests. Everything is accessible through the `vars` or `locals` namespace.
The difference between variables and locals is, that you can use the jinja syntax for locals like merging two variables together or converting maps into json.

Examples:
```
# Access locals
{{ locals.foo.bar }}

# Access variables
{{ vars.foo.bar }}
```

## Configuration
To to [Configuration](CONFIGURATION.md) for a whole configuration guide.