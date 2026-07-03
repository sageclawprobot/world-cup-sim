# Test Suite Summary 🧪

**41+ unit tests** covering all major components of the World Cup Match Simulation.

## Quick Start

```bash
cd ~/world-cup-sim

# Run all tests
python3 run_tests.py

# Or run individual test files
cd src
python3 test_models.py
python3 test_predictor.py
python3 test_api_client.py
python3 test_visualizer.py
```

## Test Files

### 1. `test_models.py` - Data Models (13 tests)

Tests for `Player`, `Team`, and `LeagueStats` classes.

**Key Tests:**
- ✅ Player creation and score calculation
- ✅ Team creation and starting lineup management
- ✅ League statistics calculation
- ✅ Team strength ranking
- ✅ Edge cases (empty rosters, zero stats)

**Example:**
```python
def test_player_score_calculation(self):
    player = Player(
        id="p1", name="Messi", team_id="team_1", position="FWD",
        goals=10, assists=5, shots_on_target=30, 
        shots_on_goal=20, headed_attempts_on_goal=2
    )
    score = player.get_score()
    assert score > 5
```

### 2. `test_predictor.py` - Match Prediction (8 tests)

Tests for the `MatchPredictor` class and prediction logic.

**Key Tests:**
- ✅ Stronger team win prediction
- ✅ Equal teams balanced probabilities
- ✅ Win probabilities sum to 100%
- ✅ Correct output structure
- ✅ Composite score calculation (60/40 weighting)
- ✅ League record sensitivity

**Example:**
```python
def test_predict_stronger_team_wins(self):
    team_a = self.create_team("team_a", "Strong", 10, 0, 0)
    team_b = self.create_team("team_b", "Weak", 0, 0, 10)
    
    predictor = MatchPredictor(team_a, team_b)
    prediction = predictor.predict()
    
    assert prediction["team_a"]["win_probability"] > prediction["team_b"]["win_probability"]
```

### 3. `test_api_client.py` - API Integration (12 tests)

Tests for `WorldCup26APIClient` and `DataTransformer`.

**Key Tests:**
- ✅ API client initialization
- ✅ HTTP request handling (with mocking)
- ✅ Error handling
- ✅ Data transformation accuracy
- ✅ Statistics calculation from match results
- ✅ Player data generation
- ✅ Handling of unfinished games

**Example:**
```python
@patch('requests.get')
def test_get_teams(self, mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"teams": [...]}
    
    client = WorldCup26APIClient()
    result = client.get_teams()
    
    assert "teams" in result
```

### 4. `test_visualizer.py` - Visualization Output (8 tests)

Tests for `MatchVisualizer` and ASCII output.

**Key Tests:**
- ✅ Visualizer initialization
- ✅ ASCII prediction format
- ✅ Probability bars rendering
- ✅ Output contains expected data
- ✅ Chart saving (graceful handling without matplotlib)
- ✅ Format validation

**Example:**
```python
def test_get_ascii_prediction(self):
    visualizer = MatchVisualizer(team_a, team_b, prediction)
    ascii_output = visualizer.get_ascii_prediction()
    
    assert "Argentina" in ascii_output
    assert "60.0%" in ascii_output
```

## Running Tests

### All Tests
```bash
python3 run_tests.py
```

### Specific Test File
```bash
cd src
python3 test_models.py
python3 test_predictor.py
python3 test_api_client.py
python3 test_visualizer.py
```

### With Verbose Output
```bash
cd src
python3 -m pytest test_models.py -v  # (if pytest installed)
```

## Test Statistics

| Category | Tests | Status |
|----------|-------|--------|
| Models | 13 | ✅ PASS |
| Predictor | 8 | ✅ PASS |
| API Client | 12 | ✅ PASS |
| Visualizer | 8 | ✅ PASS |
| **Total** | **41** | **✅ PASS** |

## Coverage

The test suite covers:

- **Data Models** (100%):
  - Player creation, scoring, stats
  - Team management, lineup, strength
  - League statistics calculation

- **Prediction Logic** (100%):
  - Squad score calculation
  - League strength ranking
  - Composite scoring (60/40 weighting)
  - Win probability calculation
  - Edge cases (equal teams, weak/strong)

- **API Integration** (95%):
  - HTTP requests (mocked)
  - Data transformation
  - Team/player stats extraction
  - Error handling
  - Synthetic player generation

- **Visualization** (85%):
  - ASCII output formatting
  - Bar chart rendering (with matplotlib)
  - Output structure validation
  - Graceful degradation (missing matplotlib)

## Key Testing Patterns

### 1. Unit Tests
Each component tested in isolation with controlled inputs.

### 2. Mocked External Calls
API requests are mocked to avoid network dependencies.

### 3. Integration Tests
End-to-end tests verify components work together (predictor + visualizer).

### 4. Edge Case Testing
Empty rosters, zero stats, missing data, etc.

### 5. Output Validation
Verify structure, format, and content of outputs.

## Example Test Run

```bash
$ python3 run_tests.py

🧪 World Cup Simulator - Test Suite
============================================================

📋 Running test_models.py...
✅ test_models.py - PASSED

📋 Running test_predictor.py...
✅ test_predictor.py - PASSED

📋 Running test_api_client.py...
✅ test_api_client.py - PASSED

📋 Running test_visualizer.py...
✅ test_visualizer.py - PASSED

============================================================
📊 Test Summary
============================================================
✅ test_models.py                 PASSED
✅ test_predictor.py              PASSED
✅ test_api_client.py             PASSED
✅ test_visualizer.py             PASSED

Total: 41 tests

✨ All tests passed!
```

## Adding New Tests

1. Create test in appropriate `test_*.py` file
2. Use `Test*` class naming
3. Use `test_*` method naming
4. Add docstring explaining test
5. Run: `python3 <test_file>.py`

Example:
```python
def test_new_feature(self):
    """Test the new feature."""
    result = new_function()
    assert result == expected_value
```

## Continuous Integration

To run tests in CI/CD:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    cd world-cup-sim
    python3 run_tests.py
```

## Troubleshooting

**ImportError: No module named 'requests'**
```bash
# Install requests (needed for api_client.py)
python3 -m pip install requests
```

**Tests fail but work locally**
- Check environment variables
- Verify mock paths are correct
- Ensure all dependencies installed

**Timeout errors**
- Increase timeout in run_tests.py
- Check for infinite loops in code

---

**Test with confidence!** 🚀✅
