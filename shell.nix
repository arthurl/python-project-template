{ pkgs ? import <nixpkgs> { } }:
let my-texlive = pkgs.texlive.combine {
     inherit (pkgs.texlive)
       # for ipynb -> latex -> pdf conversion
       latexmk scheme-small tcolorbox environ adjustbox collectbox titling enumitem rsfs pdfcol soul ucs
       # for markdown template
       csquotes xpatch inconsolata cabin fontaxes xcharter xstring newtx cleveref;
   };
in

pkgs.mkShell {
  buildInputs = [
    pkgs.python3 pkgs.poetry
    my-texlive
    pkgs.libxml2.dev pkgs.libxslt.dev pkgs.zlib pkgs.zeromq pkgs.nodejs
  ];

  CFLAGS = "-I${pkgs.libxml2.dev}/include/libxml2";
  LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib.outPath}/lib";
}
