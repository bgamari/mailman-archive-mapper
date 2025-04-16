{
  description = "Flake utils demo";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-24.11";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs { inherit system; overlays = [ self.overlays.default ]; };
      in {
        packages = rec {
          default = pkgs.mailman-archive-mapper;
        };
        apps = rec {
          mailman-archive-mapper = flake-utils.lib.mkApp { drv = self.packages.${system}.mailman-archive-mapper; };
          default = mailman-archive-mapper;
        };
      }) // {
        overlays.default = self2: super2: {
          mailman-archive-mapper =
            self2.mailmanPackages.hyperkitty.pythonModule.pkgs.callPackage ./mapper.nix {
              inherit (self2) mailmanPackages;
            };
        };
      };
}
