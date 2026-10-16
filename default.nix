let
  pkgs = import <nixpkgs> { };
in
pkgs.mkShell {
  packages = with pkgs; [
    mypy
    prek
    python314
    uv
  ];
}
