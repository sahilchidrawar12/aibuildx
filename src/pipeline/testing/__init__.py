"""Testing module for regression tests and validation."""

from .test_projects import (
    create_simple_project_1,
    create_simple_project_2,
    create_medium_project_1,
    create_medium_project_2,
    create_hard_project_1,
    create_hard_project_2,
    create_most_complex_project_1,
    create_most_complex_project_2,
    create_most_complex_project_3,
    create_most_complex_project_4,
    create_all_test_projects,
)

from .regression_test_harness import (
    RegressionTestHarness,
    ProjectTestResult,
    DetailingMetrics,
    StageMetrics,
)

__all__ = [
    # Test projects
    "create_simple_project_1",
    "create_simple_project_2",
    "create_medium_project_1",
    "create_medium_project_2",
    "create_hard_project_1",
    "create_hard_project_2",
    "create_most_complex_project_1",
    "create_most_complex_project_2",
    "create_most_complex_project_3",
    "create_most_complex_project_4",
    "create_all_test_projects",
    # Test harness
    "RegressionTestHarness",
    "ProjectTestResult",
    "DetailingMetrics",
    "StageMetrics",
]
