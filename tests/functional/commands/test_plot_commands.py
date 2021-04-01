#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Perform a functional test of the plot command."""
import pytest

import orion.core.cli


def test_no_args(capsys):
    """Test that help is printed when no args are given."""
    with pytest.raises(SystemExit):
        orion.core.cli.main(["plot"])

    captured = capsys.readouterr().err

    assert "usage:" in captured
    assert "the following arguments are required: kind" in captured
    assert "Traceback" not in captured


def test_no_name(capsys):
    """Try to run the command without providing an experiment name"""
    returncode = orion.core.cli.main(["plot", "lpi"])
    assert returncode == 1

    captured = capsys.readouterr().err

    assert captured == "Error: No name provided for the experiment.\n"