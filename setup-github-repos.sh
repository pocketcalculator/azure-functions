#!/bin/bash

# Azure Functions GitHub Setup Script
# This script initializes each Azure Function directory as a separate git repository

echo "🚀 Setting up Azure Functions for GitHub..."
echo

# Array of directories to initialize (excluding the one already on GitHub)
directories=(
    "cosmosDBTrigger"
    "eventHubsTrigger" 
    "httpTrigger"
    "iotHub2cosmosDBTrigger"
    "iot_datamover_cosmosdb"
    "iothub2cosmosdb"
    "test_function"
    "test_function_2"
)

for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "📁 Setting up $dir..."
        cd "$dir"
        
        # Initialize git repository
        git init
        echo "✅ Initialized git repository"
        
        # Add all files
        git add .
        echo "✅ Added files to staging"
        
        # Create initial commit
        git commit -m "Initial commit: Azure Function $dir with security protections"
        echo "✅ Created initial commit"
        
        # Set default branch to main
        git branch -M main
        echo "✅ Set default branch to main"
        
        echo "🎯 To connect to GitHub, run:"
        echo "   gh repo create $dir --public --source=. --push"
        echo "   OR manually create repo on GitHub and run:"
        echo "   git remote add origin https://github.com/YOUR_USERNAME/$dir.git"
        echo "   git push -u origin main"
        echo
        
        cd ..
    else
        echo "⚠️  Directory $dir not found, skipping..."
    fi
done

echo "🎉 Setup complete!"
echo
echo "📋 Summary:"
echo "- eventhub2cosmosdb_function: Already on GitHub ✅"
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "- $dir: Ready for GitHub 🚀"
    fi
done
echo
echo "💡 Next steps:"
echo "1. Create GitHub repositories for each function"
echo "2. Connect each local repository to its GitHub remote"
echo "3. Push the code to GitHub"