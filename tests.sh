#!/bin/bash
# Run all tests for World Cup Simulation

set -e

cd "$(dirname "$0")/src"

echo "🧪 Running World Cup Simulator Tests"
echo "===================================="
echo ""

# Check if pytest is available
if ! command -v pytest &> /dev/null; then
    echo "⚠️  pytest not found, trying python3 -m pytest..."
    PYTEST_CMD="python3 -m pytest"
else
    PYTEST_CMD="pytest"
fi

# Run all tests
echo "📋 Test Files:"
echo "  - test_models.py (Player, Team, LeagueStats)"
echo "  - test_predictor.py (Match prediction logic)"
echo "  - test_api_client.py (API client & data transformation)"
echo "  - test_visualizer.py (Visualization output)"
echo ""

$PYTEST_CMD test_models.py -v
echo ""

$PYTEST_CMD test_predictor.py -v
echo ""

$PYTEST_CMD test_api_client.py -v
echo ""

$PYTEST_CMD test_visualizer.py -v
echo ""

echo "✅ All tests completed!"
echo ""
echo "📊 Test Coverage Summary:"
$PYTEST_CMD test_*.py --tb=short -q 2>/dev/null || true
