param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^i-[0-9a-f]+$')]
    [string]$InstanceId,

    [string]$StackName = "OpsPilotAutomation"
)

$ErrorActionPreference = "Stop"

$TemplatePath = Join-Path $PSScriptRoot "..\infrastructure\cloudformation\opspilot-automation.yaml"
$ResolvedTemplatePath = (Resolve-Path $TemplatePath).Path

Write-Host "Validating OpsPilot CloudFormation template..."
aws cloudformation validate-template --template-body "file://$($ResolvedTemplatePath.Replace('\', '/'))" | Out-Null

Write-Host "Deploying stack '$StackName'..."
aws cloudformation deploy `
    --template-file $ResolvedTemplatePath `
    --stack-name $StackName `
    --parameter-overrides "EC2InstanceId=$InstanceId" `
    --capabilities CAPABILITY_IAM `
    --no-fail-on-empty-changeset

if ($LASTEXITCODE -ne 0) {
    throw "CloudFormation deployment failed."
}

Write-Host "Deployment completed. Stack outputs:"
aws cloudformation describe-stacks `
    --stack-name $StackName `
    --query "Stacks[0].Outputs" `
    --output table
