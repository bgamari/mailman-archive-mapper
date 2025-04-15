{
  description = "Flake utils demo";

  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in
      {
        packages = rec {
          mailman-archive-mapper = pkgs.python3Packages.callPackage ./mapper.nix {
            inherit (pkgs) mailmanPackages;
          };
          default = mailman-archive-mapper;
        };
        apps = rec {
          mailman-archive-mapper = flake-utils.lib.mkApp { drv = self.packages.${system}.mailman-archive-mapper; };
          default = mailman-archive-mapper;
        };
      }
    );
}
