# References:
# https://github.com/NixOS/nixpkgs/blob/master/doc/languages-frameworks/python.section.md
# http://datakurre.pandala.org/2015/10/nix-for-python-developers.html
# (not used here, for future consideration) https://github.com/datakurre/setup.nix

{ pkgsF ? import <nixpkgs> }:

let p = pkgsF {
      #config = {
      #  allowUnfree = true;
      #  allowBroken = false;
      #  allowUnsupportedSystem = (pkgsF {}).stdenv.isDarwin;
      #};
    };
    msg_parser = python-packages: import ./msg_parser.nix {
                      inherit (p) lib;
                      inherit (python-packages) buildPythonPackage fetchPypi olefile;
                    };
    python-deps = python-packages: [
      python-packages.pytest
      python-packages.numpy
      python-packages.sortedcontainers
      (msg_parser python-packages)
    ];
in

p.python39.withPackages python-deps
