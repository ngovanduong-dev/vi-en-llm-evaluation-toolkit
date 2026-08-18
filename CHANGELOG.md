# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
The project does not yet have a tagged release history.

## [Unreleased]

### Added

- PEP 621 package metadata, an editable development extra, and the `vi-en-eval`
  console command.
- Ruff, strict mypy, branch coverage, Bandit, dependency audit, and package build
  quality gates.

### Changed

- Protected private and local evaluation material through ignored data and
  artifact directories.
- Migrated production modules from `src.*` imports to the installable
  `vi_en_eval` package and expanded CI across Python 3.11, 3.12, and 3.13.
