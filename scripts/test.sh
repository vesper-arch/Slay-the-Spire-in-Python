#!/usr/bin/env bash

# Convenience script for running tests locally.
poetry run pytest -s --tb=short --cov-report html --cov-report xml:coverage.xml --cov=.