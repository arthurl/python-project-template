# Python project skeleton

## Environment setup

Poetry is used. See https://www.youtube.com/watch?v=TbIHRHy7_JM and
https://www.tweag.io/blog/2020-08-12-poetry2nix (and also
https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
and https://nixos.wiki/wiki/Python).

Direnv is used to set the correct virtualenv.

Upgrade to latest packages:

    poetry add --dev pytest@latest pylint@latest flake8@latest flake8-black@latest pyright@latest data-science-types@latest types-requests@latest

Run:

    poetry run arthurexec
