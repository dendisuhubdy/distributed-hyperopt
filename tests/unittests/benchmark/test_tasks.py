#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for :mod:`orion.benchmark.task`."""

from orion.benchmark.task import Branin, CarromTable, EggHolder, RosenBrock


class TestBranin():
    """Test benchmark task branin"""

    def test_creation(self):
        """Test creation"""
        branin = Branin(2)
        assert branin.max_trials == 2
        assert branin.configuration == {'orion-benchmark-task-branin-Branin': {'max_trials': 2}}

    def test_bb_function(self):
        """Test to get task function"""
        branin = Branin(2)
        bfunc = branin.get_blackbox_function()

        assert callable(bfunc)

        objectives = bfunc([1, 2])
        assert type(objectives[0]) == dict

    def test_search_space(self):
        """Test to get task search space"""
        branin = Branin(2)

        assert branin.get_search_space() == {'x': 'uniform(0, 1, shape=2)'}


class TestCarromTable():
    """Test benchmark task CarromTable"""

    def test_creation(self):
        """Test creation"""
        branin = CarromTable(2)
        assert branin.max_trials == 2
        assert branin.configuration == {'orion-benchmark-task-carromtable-CarromTable':
                                        {'max_trials': 2}}

    def test_bb_function(self):
        """Test to get task function"""
        carrom = CarromTable(2)
        bfunc = carrom.get_blackbox_function()

        assert callable(bfunc)

        objectives = bfunc([1, 2])
        assert type(objectives[0]) == dict

    def test_search_space(self):
        """Test to get task search space"""
        carrom = CarromTable(2)

        assert carrom.get_search_space() == {'x': 'uniform(-10, 10, shape=2)'}


class TestEggHolder():
    """Test benchmark task EggHolder"""

    def test_creation(self):
        """Test creation"""
        branin = EggHolder(max_trials=2, dim=3)
        assert branin.max_trials == 2
        assert branin.configuration == {'orion-benchmark-task-eggholder-EggHolder':
                                        {'dim': 3, 'max_trials': 2}}

    def test_bb_function(self):
        """Test to get task function"""
        egg = EggHolder(2)
        bfunc = egg.get_blackbox_function()

        assert callable(bfunc)

        objectives = bfunc([1, 2])
        assert type(objectives[0]) == dict

    def test_search_space(self):
        """Test to get task search space"""
        egg = EggHolder(2)

        assert egg.get_search_space() == {'x': 'uniform(-512, 512, shape=2)'}


class TestRosenBrock():
    """Test benchmark task RosenBrock"""

    def test_creation(self):
        """Test creation"""
        branin = RosenBrock(max_trials=2, dim=3)
        assert branin.max_trials == 2
        assert branin.configuration == {'orion-benchmark-task-rosenbrock-RosenBrock':
                                        {'dim': 3, 'max_trials': 2}}

    def test_bb_function(self):
        """Test to get task function"""
        rb = RosenBrock(2)
        bfunc = rb.get_blackbox_function()

        assert callable(bfunc)

        objectives = bfunc([1, 2])
        assert type(objectives[0]) == dict

    def test_search_space(self):
        """Test to get task search space"""
        rb = RosenBrock(2)
        assert rb.get_search_space() == {'x': 'uniform(-5, 10, shape=2)'}