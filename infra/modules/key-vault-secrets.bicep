@description('Key Vault name')
param vaultName string

@description('Azure OpenAI endpoint to store in Key Vault')
param azureOpenAiEndpoint string

@description('Application Insights connection string to store in Key Vault')
@secure()
param appInsightsConnectionString string

resource vault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: vaultName
}

resource azureOpenAiEndpointSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${vault.name}/azure-openai-endpoint'
  properties: {
    value: azureOpenAiEndpoint
  }
}

resource appInsightsConnectionStringSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  name: '${vault.name}/appinsights-connection-string'
  properties: {
    value: appInsightsConnectionString
  }
}

output azureOpenAiEndpointSecretName string = azureOpenAiEndpointSecret.name
output appInsightsConnectionStringSecretName string = appInsightsConnectionStringSecret.name
