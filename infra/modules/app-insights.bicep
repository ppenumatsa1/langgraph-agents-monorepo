@description('App Insights name')
param name string

@description('Location')
param location string

@description('Log Analytics workspace id')
param workspaceId string

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: workspaceId
  }
}

@secure()
output connectionString string = appInsights.properties.ConnectionString
