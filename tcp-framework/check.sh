#!/bin/env bash

uv run ruff format
uv run mypy . --disallow-untyped-defs --warn-redundant-casts --strict-equality --disallow-untyped-calls --disallow-any-unimported
