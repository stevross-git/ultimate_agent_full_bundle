#!/bin/bash
# Dynamic memory checker and model suggestions

AVAILABLE_GB=$(free -g | awk 'NR==2{printf "%.1f", $7}')
AVAILABLE_MB=$(free -m | awk 'NR==2{printf "%d", $7}')

echo "💾 Available Memory: ${AVAILABLE_GB}GB (${AVAILABLE_MB}MB)"

if [ "$AVAILABLE_MB" -gt 8000 ]; then
    echo "🚀 High memory available! You can run large models:"
    echo "   ollama pull llama3.1:8b"
    echo "   ollama pull codellama:7b"
elif [ "$AVAILABLE_MB" -gt 4000 ]; then
    echo "⚡ Good memory available! You can run medium models:"
    echo "   ollama pull llama3.2:3b"
    echo "   ollama pull codegemma:7b"
elif [ "$AVAILABLE_MB" -gt 2500 ]; then
    echo "💡 Limited memory. Use efficient models:"
    echo "   ollama pull phi3:mini"
    echo "   ollama pull tinyllama:1.1b"
else
    echo "⚠️ Very limited memory. Use tiny models only:"
    echo "   ollama pull tinyllama:1.1b"
fi

echo ""
echo "Current models:"
ollama list
