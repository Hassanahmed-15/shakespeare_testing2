#!/bin/bash

# Kill any existing server on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

echo "🚀 Starting Shakespeare Digital Variorum server..."
echo "📝 Open http://localhost:8000 in your browser"
echo ""
echo "⚠️  Note: The Netlify functions won't work with this simple server."
echo "   The UI will load, but API calls will fail."
echo "   For full functionality, install Netlify CLI: npm install -g netlify-cli"
echo "   Then run: netlify dev"
echo ""

cd "$(dirname "$0")"
python3 -m http.server 8000

