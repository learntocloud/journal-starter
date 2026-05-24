targetScope = 'resourceGroup'

@description('Azure region for all resources.')
param location string = resourceGroup().location

@description('Container app name.')
param containerAppName string = 'journal-api'

@description('Container Apps managed environment name.')
param environmentName string = '${containerAppName}-env'

@description('Log Analytics workspace name.')
param logAnalyticsName string = '${containerAppName}-logs'

@description('Azure Container Registry name. Must be globally unique.')
param containerRegistryName string = 'cr${uniqueString(resourceGroup().id)}'

@description('Initial image used until azd deploy pushes the application image.')
param imageName string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('azd service name from azure.yaml.')
param serviceName string = 'api'

@description('Database URL. Defaults to SQLite on container-local ephemeral storage for the cheapest learning deployment.')
param databaseUrl string = 'sqlite:////tmp/journal.db'

@secure()
@description('OpenAI-compatible API key. Use a real key for /analyze, or placeholder if you only need the CRUD API.')
param openAiApiKey string

@description('OpenAI-compatible base URL.')
param openAiBaseUrl string = 'https://models.inference.ai.azure.com'

@description('OpenAI-compatible model name.')
param openAiModel string = 'gpt-4o-mini'

@description('Minimum replicas. Keep 0 for scale-to-zero.')
@minValue(0)
param minReplicas int = 0

@description('Maximum replicas. Keep 1 for SQLite so only one container writes to the database file.')
@minValue(1)
param maxReplicas int = 1

@description('Container CPU allocation.')
@allowed([
  '0.25'
  '0.5'
  '0.75'
  '1'
])
param cpu string = '0.25'

@description('Container memory allocation.')
@allowed([
  '0.5Gi'
  '1Gi'
  '1.5Gi'
  '2Gi'
])
param memory string = '0.5Gi'

var tags = {
  'azd-service-name': serviceName
}

resource registry 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: true
  }
}

resource logs 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: environmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logs.properties.customerId
        sharedKey: logs.listKeys().primarySharedKey
      }
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    managedEnvironmentId: environment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
      secrets: [
        {
          name: 'openai-api-key'
          value: openAiApiKey
        }
        {
          name: 'acr-password'
          value: registry.listCredentials().passwords[0].value
        }
      ]
      registries: [
        {
          server: registry.properties.loginServer
          username: registry.listCredentials().username
          passwordSecretRef: 'acr-password'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: imageName
          env: [
            {
              name: 'DATABASE_URL'
              value: databaseUrl
            }
            {
              name: 'OPENAI_API_KEY'
              secretRef: 'openai-api-key'
            }
            {
              name: 'OPENAI_BASE_URL'
              value: openAiBaseUrl
            }
            {
              name: 'OPENAI_MODEL'
              value: openAiModel
            }
          ]
          resources: {
            cpu: json(cpu)
            memory: memory
          }
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = registry.properties.loginServer
output AZURE_CONTAINER_APP_NAME string = app.name
output url string = 'https://${app.properties.configuration.ingress.fqdn}'
