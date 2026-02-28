#!/bin/bash

# Y.S.M AI - TinyLlama Backup Setup Script
# This installs the backup AI engine for offline/independent operation

echo "🤖 Y.S.M AI - Installing Backup Engine (TinyLlama)"
echo "=============================================="
echo ""

# Step 1: Install llama-cpp-python
echo "📦 Step 1: Installing llama-cpp-python..."
pip install llama-cpp-python --quiet

# Step 2: Create cache directory
echo "📁 Step 2: Creating model cache directory..."
mkdir -p /home/tele/.cache

# Step 3: Download TinyLlama model
echo "⬇️  Step 3: Downloading TinyLlama GGUF model..."
echo "   (This may take 2-3 minutes, file size: ~600MB)"

cd /home/tele/.cache

# Download from HuggingFace
wget -q --show-progress \
  https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf \
  -O tinyllama.gguf

if [ $? -eq 0 ]; then
    echo "✅ TinyLlama model downloaded successfully!"
else
    echo "❌ Download failed. You can manually download from:"
    echo "   https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF"
    exit 1
fi

# Step 4: Test the installation
echo ""
echo "🧪 Step 4: Testing backup AI..."
python3 << 'EOF'
try:
    from ai.local_llm import get_local_service
    local_ai = get_local_service()
    
    if local_ai.is_available():
        print("✅ Backup AI is ONLINE and ready!")
        test_response = local_ai.ask_tutor("Hello, are you working?")
        print(f"   Test Response: {test_response[:100]}...")
    else:
        print("⚠️  Backup AI loaded but model not available")
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
EOF

echo ""
echo "=============================================="
echo "🎉 Setup Complete!"
echo ""
echo "Your AI now has TWO engines:"
echo "  1. Primary: Google Gemini (fast, powerful)"
echo "  2. Backup: TinyLlama (slower, but 100% independent)"
echo ""
echo "If Gemini fails, TinyLlama will automatically activate."
echo "=============================================="
