#!/bin/bash
# Memory Management and Model Selection Solution

echo "🧠 Memory Analysis & Solution"
echo "============================"

echo "📊 Current Memory Status:"
free -h
echo ""

echo "🔍 What's using your memory:"
echo "Top memory consumers:"
ps aux --sort=-%mem | head -10

echo ""
echo "🎯 Memory Solutions:"
echo "=================="

echo "1️⃣ Quick Fix - Download smaller models that fit your available memory:"
echo ""

# Remove the large models that don't fit
echo "Removing models that are too large for current available memory..."
ollama rm gemma2:latest 2>/dev/null || echo "gemma2:latest not found or already removed"
ollama rm llama3.2:latest 2>/dev/null || echo "llama3.2:latest not found or already removed"

echo ""
echo "📥 Downloading models that fit your available memory (2.7GB):"

# Download smaller models that will definitely work
echo "Downloading TinyLlama (1.1B parameters, ~1GB)..."
ollama pull tinyllama:1.1b

echo ""
echo "Downloading Phi-3 Mini (3.8B parameters, ~2.3GB)..."
ollama pull phi3:mini

echo ""
echo "🧪 Testing the new smaller models:"

echo ""
echo "1️⃣ Testing TinyLlama (very lightweight):"
ollama run tinyllama:1.1b "Hello! Please say 'TinyLlama working' if you understand this."

echo ""
echo "2️⃣ Testing Phi-3 Mini (Microsoft's efficient model):"
ollama run phi3:mini "Hello! Please say 'Phi-3 working' and tell me what 2+2 equals."

echo ""
echo "💡 Memory Optimization Tips:"
echo "==========================="

echo ""
echo "🔧 To free up more memory for larger models:"
echo "1. Close unnecessary applications:"
echo "   • Web browsers with many tabs"
echo "   • IDEs or text editors"
echo "   • Other development tools"
echo ""
echo "2. Check for memory leaks:"
echo "   sudo systemctl restart ollama"
echo ""
echo "3. Increase swap space (if needed):"
echo "   sudo fallocate -l 4G /swapfile"
echo "   sudo chmod 600 /swapfile"
echo "   sudo mkswap /swapfile"
echo "   sudo swapon /swapfile"
echo ""

echo "📋 Model Recommendations for Your System:"
echo "========================================"
echo ""
echo "✅ Models that work with 2.7GB available memory:"
echo "   • tinyllama:1.1b      (~1GB)  - Very fast, good for basic tasks"
echo "   • phi3:mini           (~2.3GB) - Better quality, still efficient"
echo "   • qwen2:1.5b          (~1.5GB) - Good balance"
echo ""
echo "⚠️ Models for when you have 4GB+ available:"
echo "   • llama3.2:3b         (~3.4GB) - Your original model"
echo "   • codegemma:2b        (~2.8GB) - For programming"
echo ""
echo "🚀 Models for when you have 8GB+ available:"
echo "   • codellama:7b        (~7GB)   - Excellent for programming"
echo "   • llama3.1:8b         (~8GB)   - Latest general model"
echo ""

echo "🔄 Dynamic Memory Check Function:"
echo "================================"

cat << 'SCRIPT_EOF' > check_memory_and_suggest.sh
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
SCRIPT_EOF

chmod +x check_memory_and_suggest.sh

echo ""
echo "✅ Created memory checker script: ./check_memory_and_suggest.sh"
echo "   Run it anytime to check available memory and get model suggestions"

echo ""
echo "🎯 Next Steps:"
echo "============="
echo "1. Test the new smaller models above"
echo "2. Close unnecessary applications to free memory"
echo "3. Run ./check_memory_and_suggest.sh to see what models you can use"
echo "4. Once working, integrate with Ultimate Agent using the smaller models"

echo ""
echo "📱 Alternative: Restart with more available memory:"
echo "================================================="
echo "If you want to use larger models:"
echo "1. Save your work and close applications"
echo "2. Restart the system to free up memory"
echo "3. Check available memory with: free -h"
echo "4. Then download appropriately sized models"

echo ""
echo "💡 Pro Tip: TinyLlama and Phi-3 Mini are surprisingly capable!"
echo "   They're perfect for testing the integration, and you can always"
echo "   upgrade to larger models later when you have more memory available."
