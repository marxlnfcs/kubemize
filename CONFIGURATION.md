# Kubemize Configuration

# kubemize.yaml
| Field     | Type                                       | Default | Description |
|-----------|--------------------------------------------|---------|-------------|
| extends   | Array(string, [FilePattern](#FilePattern)) |         |             |
| hooks     | [Hooks](#Hooks)                            |         |             |
| namespace | string                                     |         |             |
| helm      | [Helm](#Helm)                              |         |             |
| kubectl   | [Kubectl](#Kubectl)                        |         |             |
| locals    | [Locals](#Locals)                          |         |             |
| variables | [Variables](#Variables)                    |         |             |

# FilePattern
File patterns are simple GLOB strings

| Field    | Type     | Default | Description  |
|----------|----------|---------|--------------|
| patterns | string[] |         |              |

# CliArguments
| Field   | Type     | Default | Description                                                 |
|---------|----------|---------|-------------------------------------------------------------|
| global  | KeyValue |         | Applies these arguments to either apply or destroy commands |
| apply   | KeyValue |         | Applies these arguments to apply commands                   |
| destroy | KeyValue |         | Applies these arguments to destroy commands                 |

# Hooks
With hooks, you can run scripts before and after certain actions

| Field           | Type                                       | Default | Description        |
|-----------------|--------------------------------------------|---------|--------------------|
| pre_all         | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_all        | Array(string, [FilePattern](#FilePattern)) |         |                    |
| pre_apply       | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_apply      | Array(string, [FilePattern](#FilePattern)) |         |                    |
| pre_template    | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_template   | Array(string, [FilePattern](#FilePattern)) |         |                    |
| pre_standalone  | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_standalone | Array(string, [FilePattern](#FilePattern)) |         |                    |
| pre_plan        | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_plan       | Array(string, [FilePattern](#FilePattern)) |         |                    |
| pre_destroy     | Array(string, [FilePattern](#FilePattern)) |         |                    |
| post_destroy    | Array(string, [FilePattern](#FilePattern)) |         |                    |

# Helm
| Field        | Type                                | Default | Description                                     |
|--------------|-------------------------------------|---------|-------------------------------------------------|
| arguments    | [CliArguments](#CliArguments)       |         | CLI arguments to use when running helm commands |
| repositories | [HelmRepository[]](#HelmRepository) |         |                                                 |
| releases     | [HelmRelease[]](#HelmRelease)       |         |                                                 |

# HelmRepository
| Field           | Type    | Default | Description                            |
|-----------------|---------|---------|----------------------------------------|
| **name**        | string  |         | Name of the repository (for reference) |
| **url**         | string  |         | URL to the repository                  |
| username        | string  |         |                                        |
| password        | string  |         |                                        |
| passCredentials | boolean |         |                                        |
| certFile        | string  |         |                                        |
| keyFile         | string  |         |                                        |
| keyRing         | string  |         |                                        |
| verify          | bool    |         |                                        |

# HelmRelease
| Field      | Type                                                                                                                                                                                                | Default        | Description                                                                                            |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|--------------------------------------------------------------------------------------------------------|
| **name**   | string                                                                                                                                                                                              |                | Name of the release                                                                                    |
| **chart**  | string                                                                                                                                                                                              |                | Name of the chart (&lt;repository_name&gt;/&lt;chart_name&gt;), path to the chart directory or OCI url |
| version    | string                                                                                                                                                                                              |                | Chart version                                                                                          |
| namespace  | string                                                                                                                                                                                              | vars.namespace |                                                                                                        |
| arguments  | [CliArguments](#CliArguments)                                                                                                                                                                       |                | CLI arguments to use when running helm commands (will be merged with the global arguments)             |
| values     | Array(str, [FilePattern](#FilePattern))                                                                                                                                                             |                |                                                                                                        |
| set        | KeyValue: str, [HelmReleaseSetFile](#HelmReleaseSetFile), [HelmReleaseSetJSON](#HelmReleaseSetJSON), [HelmReleaseSetLiteral](#HelmReleaseSetLiteral), [HelmReleaseSetString](#HelmReleaseSetString) |                |                                                                                                        |


# HelmReleaseSetFile
| Field         | Type                          | Default        | Description                                                                                |
|---------------|-------------------------------|----------------|--------------------------------------------------------------------------------------------|
| **type**      | "file"                        |                |                                                                                            |
| **path**      | string                        |                |                                                                                            |

# HelmReleaseSetJSON
| Field       | Type          | Default        | Description                                                                                |
|-------------|---------------|----------------|--------------------------------------------------------------------------------------------|
| **type**    | "json"        |                |                                                                                            |
| **data**    | object, array |                |                                                                                            |

# HelmReleaseSetLiteral
| Field       | Type      | Default        | Description                                                                                |
|-------------|-----------|----------------|--------------------------------------------------------------------------------------------|
| **type**    | "literal" |                |                                                                                            |
| **value**   | string    |                |                                                                                            |

# HelmReleaseSetString
| Field       | Type      | Default        | Description                                                                                |
|-------------|-----------|----------------|--------------------------------------------------------------------------------------------|
| **type**    | "string"  |                |                                                                                            |
| **value**   | string    |                |                                                                                            |

# Kubectl
| Field      | Type                                        | Default      | Description                                                          |
|------------|---------------------------------------------|--------------|----------------------------------------------------------------------|
| order      | string[]                                    | Namespace, * | Defines the order in which Kubernetes Manifest Kinds will be handled |
| arguments  | [CliArguments](#CliArguments)               |              | CLI arguments to use when running kubectl commands                   |
| manifests  | Array(string, [FilePattern](#FilePattern))  |              | CLI arguments to use when running kubectl commands                   |
| generators | [KubectlGenerators](#KubectlGenerators)     |              | CLI arguments to use when running kubectl commands                   |

# KubectlGenerators
| Field      | Type                                                          | Default | Description |
|------------|---------------------------------------------------------------|---------|-------------|
| configMaps | [KubectlGeneratorsConfigMap[]](#KubectlGeneratorsConfigMap)   |         |             |
| secrets    | [KubectlGeneratorsConfigMap[]](#KubectlGeneratorsConfigMap)   |         |             |

# KubectlGeneratorsConfigMap
| Field       | Type                                                                                                                                                                                                                                                                                     | Default | Description |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------|
| **name**    | string                                                                                                                                                                                                                                                                                   |         |             |
| namespace   | string                                                                                                                                                                                                                                                                                   |         |             |
| annotations | KeyValue                                                                                                                                                                                                                                                                                 |         |             |
| labels      | KeyValue                                                                                                                                                                                                                                                                                 |         |             |
| data        | KeyValue: [KubectlGeneratorsConfigMapSimple](#KubectlGeneratorsConfigMapSimple), [KubectlGeneratorsConfigMapFile](#KubectlGeneratorsConfigMapFile), [KubectlGeneratorsConfigMapJSON](#KubectlGeneratorsConfigMapJSON), [KubectlGeneratorsConfigMapYaml](#KubectlGeneratorsConfigMapYaml) |         |             |

# KubectlGeneratorsConfigMapSimple
| Field       | Type                            | Default | Description |
|-------------|---------------------------------|---------|-------------|
| **value**   | string, integer, float, boolean |         |             |

# KubectlGeneratorsConfigMapFile
| Field    | Type   | Default | Description |
|----------|--------|---------|-------------|
| **type** | "file" |         |             |
| **path** | string |         |             |

# KubectlGeneratorsConfigMapJSON
| Field    | Type          | Default | Description |
|----------|---------------|---------|-------------|
| **type** | "json"        |         |             |
| **path** | object, array |         |             |

# KubectlGeneratorsConfigMapYaml
| Field    | Type          | Default | Description |
|----------|---------------|---------|-------------|
| **type** | "yaml"        |         |             |
| **path** | object, array |         |             |

# KubectlGeneratorsSecret
| Field       | Type                                                                                                                                                                                                                                                               | Default | Description |
|-------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|-------------|
| **name**    | string                                                                                                                                                                                                                                                             |         |             |
| namespace   | string                                                                                                                                                                                                                                                             |         |             |
| annotations | KeyValue                                                                                                                                                                                                                                                           |         |             |
| labels      | KeyValue                                                                                                                                                                                                                                                           |         |             |
| type        | string                                                                                                                                                                                                                                                             | Opaque  |             |
| data        | KeyValue: [KubectlGeneratorsSecretSimple](#KubectlGeneratorsSecretSimple), [KubectlGeneratorsSecretFile](#KubectlGeneratorsSecretFile), [KubectlGeneratorsSecretJSON](#KubectlGeneratorsSecretJSON), [KubectlGeneratorsSecretYaml](#KubectlGeneratorsSecretYaml)   |         |             |

# KubectlGeneratorsSecretSimple
| Field       | Type                            | Default | Description |
|-------------|---------------------------------|---------|-------------|
| **value**   | string, integer, float, boolean |         |             |

# KubectlGeneratorsSecretFile
| Field    | Type   | Default | Description |
|----------|--------|---------|-------------|
| **type** | "file" |         |             |
| **path** | string |         |             |

# KubectlGeneratorsSecretJSON
| Field    | Type          | Default | Description |
|----------|---------------|---------|-------------|
| **type** | "json"        |         |             |
| **path** | object, array |         |             |

# KubectlGeneratorsSecretYaml
| Field    | Type          | Default | Description |
|----------|---------------|---------|-------------|
| **type** | "yaml"        |         |             |
| **path** | object, array |         |             |


# Locals
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| key   | any  |         |             |

# Variables
| Field | Type | Default | Description |
|-------|------|---------|-------------|
| key   | any  |         |             |