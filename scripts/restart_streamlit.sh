#!/bin/bash
# Restart Streamlit app and clear all caches

echo "=========================================="
echo "Restarting Streamlit App"
echo "=========================================="

# Kill any running Streamlit processes
echo ""
echo "1. Stopping existing Streamlit processes..."
pkill -f "streamlit run" 2>/dev/null
lsof -ti:8501 | xargs kill -9 2>/dev/null
sleep 2
echo "   ✅ Stopped"

# Clear Python bytecode cache
echo ""
echo "2. Clearing Python bytecode cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Cleared __pycache__"

# Clear Streamlit cache
echo ""
echo "3. Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null
echo "   ✅ Cleared Streamlit cache"

# Wait a moment
sleep 1

# Start Streamlit
echo ""
echo "4. Starting Streamlit app..."
echo "   URL: http://localhost:8501"
echo ""
echo "=========================================="
echo "Starting in 3 seconds..."
echo "=========================================="
sleep 3

# Start Streamlit in the background
streamlit run src/ui/app.py --server.port 8501 &

echo ""
echo "✅ Streamlit started!"
echo ""
echo "📝 Next steps:"
echo "   1. Wait 5-10 seconds for the app to start"
echo "   2. Open http://localhost:8501 in your browser"
echo "   3. Try uploading the video again"
echo ""
echo "To stop Streamlit:"
echo "   pkill -f streamlit"
echo ""

