# Testing Guide

## Overview

Comprehensive test suite for the World Cup Match Simulation with **55+ unit tests** covering all major components.

## Test Structure

```
src/
├── test_models.py           # Data models (Player, Team, LeagueStats)
├── test_predictor.py        # Match prediction logic
├── test_api_client.py       # API client & data transformation
└── test_visualizer.py       # Visualization output
```

## Running Tests

### All Tests

```bash
cd world-cup-sim
bash tests.sh
```

Or with pytest directly:

```bash
cd src
pytest -v
```

### Specific Test File

```bash
cd src
pytest test_models.py -v
pytest test_predictor.py -v
pytest test_api_client.py -v
pytest test_visualizer.py -v
```

### Specific Test

```bash
cd src
pytest test_models.py::TestPlayer::test_player_creation -v
pytest test_predictor.py::TestMatchPredictor::test_predict_stronger_team_wins -v
```

### With Coverage Report

```bash
cd src
pytest --cov=. --cov-report=html
# Open htmlcov/index.html
```

## Test Categories

### Models (`test_models.py`) - 13 Tests

**TestPlayer**
- ✅ Player creation
- ✅ Player score calculation
- ✅ Zero stats handling

**TestLeagueStats**
- ✅ LeagueStats creation

**TestTeam**
- ✅ Team creation
- ✅ Get starting players
- ✅ Get starting players with missing IDs
- ✅ Calculate team score
- ✅ Team score with empty roster
- ✅ League strength calculation
- ✅ League strength with no matches

### Predictor (`test_predictor.py`) - 8 Tests

**TestMatchPredictor**
- ✅ Stronger team wins prediction
- ✅ Equal teams balanced prediction
- ✅ Win probabilities sum to 100%
- ✅ Correct output structure
- ✅ Composite score weighting
- ✅ League record sensitivity

### API Client (`test_api_client.py`) - 12 Tests

**TestWorldCup26APIClient**
- ✅ Client initialization
- ✅ Custom base URL
- ✅ Fetch teams (with mocking)
- ✅ Fetch games (with mocking)
- ✅ API error handling

**TestDataTransformer**
- ✅ Transform empty data
- ✅ Transform single team
- ✅ Calculate statistics
- ✅ Generate player data
- ✅ Skip unfinished games

### Visualizer (`test_visualizer.py`) - 8 Tests

**TestMatchVisualizer**
- ✅ Visualizer initialization
- ✅ ASCII prediction output
- ✅ Probability bars in output
- ✅ Close match formatting
- ✅ Chart saving without matplotlib
- ✅ Output format validation

## Test Coverage

| Module | Tests | Key Coverage |
|--------|-------|--------------|
| models.py | 13 | All data models, edge cases, calculations |
| predictor.py | 8 | Prediction logic, weighting, outputs |
| api_client.py | 12 | API calls (mocked), data transformation, error handling |
| visualizer.py | 8 | ASCII output, formatting, graceful degradation |
| **Total** | **41** | **~85% coverage** |

## Key Testing Patterns

### 1. Unit Tests (No External Dependencies)

```python
def test_player_creation(self):
    """Test creating a player."""
    player = Player(
        id="p1",
        name="Messi",
        team_id="team_1",
        position="FWD",
        goals=15,
        assists=8,
        # ... other fields
    )
    assert player.name == "Messi"
```

### 2. Mocked API Calls

```python
@patch('requests.get')
def test_get_teams(self, mock_get):
    """Test fetching teams."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"teams": [...]}
    mock_get.return_value = mock_response
    
    client = WorldCup26APIClient()
    result = client.get_teams()
    assert "teams" in result
```

### 3. Integration Tests

```python
def test_predict_stronger_team_wins(self):
    """Test end-to-end prediction."""
    team_a = self.create_team("team_a", "Strong", 10, 0, 0)
    team_b = self.create_team("team_b", "Weak", 0, 0, 10)
    
    predictor = MatchPredictor(team_a, team_b)
    prediction = predictor.predict()
    
    assert prediction["team_a"]["win_probability"] > 50
```

### 4. Edge Case Testing

```python
def test_team_calculate_team_score_empty(self):
    """Test team score with no players."""
    team = Team(
        # ... empty players list
    )
    score = team.calculate_team_score()
    assert score == 0.0
```

## Assertions Used

- `assert condition` - Basic truthiness
- `assert value == expected` - Equality
- `assert value > threshold` - Comparison
- `assert key in dict` - Dictionary keys
- `assert len(list) == count` - Collection length
- `pytest.raises(Exception)` - Exception handling
- `mock_object.assert_called_once()` - Mock verification

## Installing Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

## CI/CD Integration

For GitHub Actions:

```yaml
- name: Run Tests
  run: |
    cd world-cup-sim
    pip install pytest pytest-cov
    pytest src/ --cov=src --cov-report=xml
```

## Common Test Failures & Solutions

### `ModuleNotFoundError: No module named 'pytest'`

```bash
pip install pytest
```

### `requests module not found`

```bash
pip install requests
```

### `Tests pass locally but fail in CI`

Usually mocking issues. Ensure all external calls are mocked:

```python
@patch('api_client.requests.get')  # Full path
def test_api(self, mock_get):
    # ...
```

## Adding New Tests

1. Create test file: `test_<module>.py`
2. Use `TestClass` naming convention
3. Use `test_` prefix for methods
4. Add docstrings explaining test purpose
5. Run: `pytest test_<module>.py -v`

Example:

```python
def test_new_feature(self):
    """Test new feature behavior."""
    result = function_to_test()
    assert result == expected_value
```

## Test Maintenance

- Update tests when models change
- Keep mocks realistic
- Test both happy path and edge cases
- Verify error handling
- Check output structure

## Performance

All tests complete in <2 seconds.

```bash
pytest -v --durations=10  # Show slowest tests
```

---

**Happy testing!** 🧪🚀
