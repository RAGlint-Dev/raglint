"""
Tests for tracking module.
"""

import pytest
from raglint.tracking import RunTracker


def test_run_tracker_initialization():
    """Test RunTracker initialization."""
    tracker = RunTracker()
    assert tracker is not None


def test_run_tracker_start_run():
    """Test starting a new run."""
    tracker = RunTracker()
    run_id = tracker.start_run(config={"provider": "mock"})
    
    assert run_id is not None
    assert isinstance(run_id, str)


def test_run_tracker_end_run():
    """Test ending a run."""
    tracker = RunTracker()
    run_id = tracker.start_run(config={"provider": "mock"})
    tracker.end_run(run_id, results={"score": 0.9})
    
    # Run should be recorded
    runs = tracker.get_runs()
    assert len(runs) > 0


def test_run_tracker_get_run():
    """Test retrieving a specific run."""
    tracker = RunTracker()
    run_id = tracker.start_run(config={"provider": "mock"})
    tracker.end_run(run_id, results={"score": 0.9})
    
    run = tracker.get_run(run_id)
    assert run is not None
    assert run.get("results", {}).get("score") == 0.9


def test_run_tracker_multiple_runs():
    """Test tracking multiple runs."""
    tracker = RunTracker()
    
    run1 = tracker.start_run(config={"provider": "mock"})
    run2 = tracker.start_run(config={"provider": "ollama"})
    
    tracker.end_run(run1, results={"score": 0.8})
    tracker.end_run(run2, results={"score": 0.9})
    
    runs = tracker.get_runs()
    assert len(runs) >= 2
