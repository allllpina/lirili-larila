{
  description = "Dev environment for lirili-larila (Python services + React frontend)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
      python = pkgs.python312;
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          python
          pkgs.uv
          pkgs.nodejs_22
        ];

        UV_PYTHON_DOWNLOADS = "never";

        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
          pkgs.stdenv.cc.cc.lib
          pkgs.zlib
        ];

        shellHook = ''
          source .venv/bin/activate
        '';
      };
    };
}
