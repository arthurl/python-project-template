# Python project skeleton

## Environment setup

Put python dependencies in `default.nix`.

`msg_parser` is included as an example of how to add arbitrary dependencies
available on pypi but not in nixpkgs.

Run `nix-build` to build interpreter. The result works as a python virtualenv
would.

Run `nix-shell` to set up environment. This would be the equivalent to
“activating” a python virtualenv.

To generate requirements.txt for other users, do `nix-shell -p pipreqs --command
'pipreqs .'`
