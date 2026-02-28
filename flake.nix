{
  description = "dark-send - A CLI Telegram client for NixOS";

  inputs.nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-25.11";

  outputs =
    { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.callPackage ./default.nix { };
    };
}
