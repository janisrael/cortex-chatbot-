#!/bin/bash
# Wait for current test to complete, then restart with improvements

cd /run/media/swordfish/Projects/development/chatbot

echo "⏳ Waiting for current test to complete..."
while ps aux | grep -q "[m]arathon_knowledge_base_test"; do
    sleep 30
    CYCLE=$(tail -50 marathon_test.log 2>/dev/null | grep -o "CYCLE [0-9]\+" | tail -1 | grep -o "[0-9]\+" || echo "?")
    echo "  Test still running... (Cycle $CYCLE/50) - $(date +%H:%M:%S)"
done

echo ""
echo "✅ Test completed!"
echo ""
echo "📊 Final Results:"
tail -200 marathon_test.log | grep -E "(FINAL GRADE|Overall|Total Tests|Passed|Failed|Email report)" | head -10
echo ""

# Wait a moment for email to be sent
sleep 5

echo "🔄 Restarting test with improvements..."
echo ""

# Remove old log
rm -f marathon_test.log

# Start new test
nohup python3 marathon_knowledge_base_test.py > marathon_test.log 2>&1 &

sleep 5

echo "✅ New test started!"
echo ""
echo "📊 Initial output:"
tail -30 marathon_test.log

echo ""
echo "Monitor with: tail -f marathon_test.log"


