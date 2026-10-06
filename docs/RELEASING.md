# Releases

A release starts only when a maintainer with repository write access pushes a
version tag such as `v0.1.0`. The workflow checks out that tag, runs the unit
suite and source compilation, and requires the tag to match the package version
in `pyproject.toml`. It then builds the source and wheel distributions and
creates a GitHub Release with generated notes and those assets.

Do not push a release tag until the corresponding source has been reviewed and
the package version has been updated. A tag push that passes CI publishes the
release immediately. The workflow has write permission only because it creates
the release; the separate pull-request CI retains read-only permissions. No
PyPI credentials or package publishing are configured.

To recover from a failed run, inspect whether the GitHub Release was created
before retrying. Do not force-move or reuse a published version tag. Release
automation has not been exercised against an actual version tag yet.
