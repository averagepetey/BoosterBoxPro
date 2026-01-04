# System Architecture - Extensibility Design

## Overview

The screenshot automation system must be designed with extensibility in mind, allowing new metrics to be added easily in the future without major refactoring.

---

## Core Design Principles

### 1. Modular Architecture

**Separation of Concerns:**
- **Data Extraction Layer**: Handles screenshot data extraction
- **Filtering Layer**: Applies all filtering rules
- **Calculation Layer**: Performs metric calculations (modular functions)
- **Storage Layer**: Handles database operations
- **API Layer**: Exposes data via endpoints
- **Frontend Layer**: Displays metrics

Each layer is independent and can be extended without affecting others.

### 2. Pluggable Calculation System

**Calculation Registry Pattern:**
```python
# Conceptual structure
calculation_registry = {
    "floor_price_1d_change_pct": calculate_floor_price_1d_change,
    "unified_volume_7d_ema": calculate_volume_7d_ema,
    "days_to_20pct_increase": calculate_days_to_20pct,
    # New metrics can be registered here
    "new_metric": calculate_new_metric,  # Easy to add
}
```

**Benefits:**
- New calculations can be added by registering a function
- No need to modify existing calculation code
- Calculations are discoverable and testable independently

### 3. Database Schema Extensibility

**Migration-Based Approach:**
- New metric fields added via database migrations
- Fields can be nullable to support gradual rollout
- Schema versioning allows safe updates
- Rollback capability if needed

**Example Migration:**
```python
# Future migration to add new metric
ALTER TABLE box_metrics_unified 
ADD COLUMN new_metric_field DECIMAL(10, 2) NULL;
```

### 4. Configuration-Driven Metrics

**Metric Definition Structure:**
```python
# Conceptual metric definition
METRIC_DEFINITIONS = {
    "unified_volume_7d_ema": {
        "name": "7-Day Volume EMA",
        "type": "calculated",
        "calculation": "calculate_volume_7d_ema",
        "dependencies": ["unified_volume_usd"],
        "database_field": "unified_volume_7d_ema",
        "display_name": "Volume (7d EMA)",
    },
    # New metrics can be defined here
}
```

**Benefits:**
- Metrics defined declaratively
- Easy to add new metrics by adding definitions
- Metadata available for API documentation
- Frontend can use metadata for display

### 5. Interface-Based Calculations

**Standard Calculation Interface:**
```python
# All calculation functions follow this pattern
def calculate_metric(
    historical_data: List[Dict],
    current_data: Dict,
    config: Optional[Dict] = None
) -> Optional[Decimal]:
    """
    Calculate metric from historical and current data.
    
    Returns:
        Calculated value or None if cannot be calculated
    """
    # Implementation
    pass
```

**Benefits:**
- Consistent function signatures
- Easy to test and validate
- Can be swapped/replaced easily
- Type hints provide clarity

---

## Adding New Metrics: Step-by-Step Process

### Step 1: Define Metric in Specification
Update `CALCULATION_SPECIFICATION.md`:
- Document the metric
- Define calculation formula
- Specify data requirements
- Document edge cases

### Step 2: Create Database Migration
Create migration file:
```python
# migrations/versions/XXX_add_new_metric.py
def upgrade():
    op.add_column('box_metrics_unified', 
                  sa.Column('new_metric', sa.Numeric(10, 2), nullable=True))
```

Run migration:
```bash
alembic upgrade head
```

### Step 3: Update Database Model
Add field to `UnifiedBoxMetrics` model:
```python
# app/models/unified_box_metrics.py
new_metric: Mapped[Optional[Decimal]] = mapped_column(
    Numeric(10, 2), nullable=True
)
```

### Step 4: Implement Calculation Function
Create calculation function:
```python
# app/services/metrics_calculator.py or new module
def calculate_new_metric(
    historical_data: List[Dict],
    current_data: Dict,
    config: Optional[Dict] = None
) -> Optional[Decimal]:
    """
    Calculate new metric based on specification.
    
    Args:
        historical_data: Historical entries
        current_data: Current day data
        config: Optional configuration
        
    Returns:
        Calculated metric value or None
    """
    # Implementation following specification
    pass
```

### Step 5: Register Calculation
Add to calculation registry:
```python
# In metrics calculator initialization
CALCULATION_REGISTRY["new_metric"] = calculate_new_metric
```

### Step 6: Integrate into Calculation Pipeline
Add to calculation pipeline:
```python
# In calculate_daily_metrics()
metrics["new_metric"] = calculate_new_metric(
    historical_data, current_data
)
```

### Step 7: Update API (Automatic)
If using dynamic field inclusion:
- API automatically includes new database fields
- No API code changes needed

If using explicit schemas:
- Update API response schemas
- Add to serialization

### Step 8: Update Frontend (Optional)
When ready to display:
- Add field to TypeScript interfaces
- Add to display components
- Update charts if needed

---

## Architecture Patterns

### Pattern 1: Strategy Pattern for Calculations

Each metric calculation is a strategy that can be selected and executed:

```python
class MetricCalculator:
    def __init__(self):
        self.calculators = {}
    
    def register(self, name: str, calculator: Callable):
        self.calculators[name] = calculator
    
    def calculate(self, name: str, *args, **kwargs):
        if name in self.calculators:
            return self.calculators[name](*args, **kwargs)
        return None
```

### Pattern 2: Pipeline Pattern for Processing

Data flows through a processing pipeline:

```python
class ProcessingPipeline:
    def __init__(self):
        self.steps = []
    
    def add_step(self, step: Callable):
        self.steps.append(step)
    
    def process(self, data):
        for step in self.steps:
            data = step(data)
        return data
```

### Pattern 3: Observer Pattern for Updates

When data changes, observers (rankings, charts, etc.) update:

```python
class DataObserver:
    def on_data_updated(self, box_id: str, metrics: Dict):
        # Update rankings
        # Update charts
        # Notify frontend
        pass
```

---

## Code Organization

### Recommended Structure

```
app/
├── services/
│   ├── metrics_calculator.py       # Core calculation engine
│   ├── calculations/                # Individual calculation modules
│   │   ├── __init__.py
│   │   ├── volume_metrics.py       # Volume calculations
│   │   ├── price_metrics.py        # Price calculations
│   │   ├── supply_metrics.py       # Supply calculations
│   │   └── derived_metrics.py      # Derived metrics
│   └── calculation_registry.py     # Registry for calculations
├── models/
│   └── unified_box_metrics.py      # Database model
└── routers/
    └── boxes.py                     # API endpoints
```

**Benefits:**
- Calculations are organized by category
- Easy to find and modify calculations
- New calculations go in appropriate module
- Clear separation of concerns

---

## Testing Extensibility

### Unit Tests for New Metrics

Each new metric should have:
- Unit tests for calculation function
- Tests for edge cases
- Tests for data requirements
- Integration tests with pipeline

### Example Test Structure

```python
def test_calculate_new_metric():
    historical_data = [...]
    current_data = {...}
    result = calculate_new_metric(historical_data, current_data)
    assert result is not None
    assert isinstance(result, Decimal)
    # More assertions
```

---

## Best Practices for Extensibility

1. **Keep Calculations Pure**: No side effects, only inputs → outputs
2. **Document Dependencies**: Each calculation should document what data it needs
3. **Handle Missing Data**: Calculations should handle None/missing values gracefully
4. **Use Type Hints**: Makes code self-documenting and catches errors early
5. **Follow Naming Conventions**: Consistent naming makes code discoverable
6. **Write Tests**: New calculations must have tests
7. **Update Documentation**: Specification must be updated when adding metrics
8. **Backward Compatibility**: New metrics shouldn't break existing functionality

---

## Migration Strategy

When adding new metrics:

1. **Phase 1: Database & Calculation**
   - Add database field (nullable)
   - Implement calculation
   - Test calculation
   - Deploy (metric calculates but may not display)

2. **Phase 2: API**
   - Verify API includes new field
   - Test API responses
   - Deploy (metric available via API)

3. **Phase 3: Frontend (Optional)**
   - Add to TypeScript interfaces
   - Add to UI components
   - Test display
   - Deploy (metric visible to users)

This phased approach allows:
- Gradual rollout
- Testing at each stage
- Rollback if issues
- No breaking changes

---

## Summary

The system architecture must support:
- ✅ Modular, pluggable calculations
- ✅ Database schema extensibility
- ✅ API automatic field inclusion
- ✅ Clear process for adding metrics
- ✅ Backward compatibility
- ✅ Testing support
- ✅ Documentation requirements

**Adding a new metric should be straightforward and not require major refactoring.**

