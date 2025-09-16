#!/bin/bash

# Deployment preparation script
echo "Preparing for deployment..."

# Clean up node_modules and cache files
echo "Cleaning up unnecessary files..."
find . -name "node_modules" -type d -exec rm -rf {} +
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".cache" -type d -exec rm -rf {} +

# Remove database files
rm -f *.db
rm -f backend/*.db

echo "Cleanup complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to GitHub"
echo "2. Deploy backend to Render"
echo "3. Deploy frontend to Vercel"
echo "4. Update environment variables"
