#!/bin/sh

# Startup script for Unified Python Prompt House Premium

echo "🐍 Starting Prompt House Premium - Unified Python Application..."

# Remove stale SSL certs that can block Neon connections
rm -rf /root/.postgresql ~/.postgresql 2>/dev/null || true
export PGSSLCERT=/tmp/.postgresql/nonexistent.crt
export PGSSLKEY=/tmp/.postgresql/nonexistent.key

# Function to handle shutdown gracefully
cleanup() {
    echo "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup TERM INT

# Apply database migrations
echo "📊 Applying database migrations..."
if [ -f "apply_admin_migration.py" ]; then
    python apply_admin_migration.py
    if [ $? -eq 0 ]; then
        echo "✅ Database migrations applied successfully"
    else
        echo "⚠️  Database migration failed, but continuing startup..."
    fi
fi

# Start the unified Python application
echo "🚀 Starting unified Python backend server on port $PORT..."
python main.py &
BACKEND_PID=$!

echo "✅ Python backend server started with PID $BACKEND_PID"
echo "🌐 Services are running:"
echo "  - Frontend available at http://localhost:$PORT/"
echo "  - API available at http://localhost:$PORT/api"
echo "  - Health check at http://localhost:$PORT/health"

# Wait for the process to exit
wait $BACKEND_PID

echo "❌ Python application has stopped, shutting down..."
cleanup
