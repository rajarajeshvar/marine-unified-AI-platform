$ErrorActionPreference = "Continue"

Write-Host "Updating .gitignore..."
Add-Content -Path "C:\Users\rajan\OneDrive\Documents\engine_failure_prediction\.gitignore" -Value "*.csv"

Write-Host "Cleaning up previous git attempt..."
Remove-Item -Recurse -Force "C:\Users\rajan\OneDrive\Documents\engine_failure_prediction\.git" -ErrorAction SilentlyContinue

Write-Host "Initializing Git Repository..."
git init

Write-Host "Adding remote origin..."
git remote add origin https://github.com/rajarajeshvar/marine-unified-AI-platform.git

Write-Host "Setting branch to main..."
git branch -M main

Write-Host "Adding files..."
git add .

Write-Host "Committing..."
git commit -m "Initial commit: Marine Unified AI Platform with ML models"

Write-Host "Pushing to GitHub..."
git push -u origin main -f
