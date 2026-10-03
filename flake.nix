{
  description = "ShadcnIOS development tools and fixed test source";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/44a91898084f46797b5fac650c7e8c9ac38c43d4";
    snapshot = {
      url = "github:pointfreeco/swift-snapshot-testing/1.18.9";
      flake = false;
    };
  };
  outputs =
    { nixpkgs, snapshot, ... }:
    let
      system = "aarch64-darwin";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          swiftlint
          swiftformat
          just
          python3
          ruff
          nixfmt
          yamllint
          actionlint
        ];
        SNAPSHOT_SOURCE = "${snapshot}";
        shellHook = ''
          unset SDKROOT
          export DEVELOPER_DIR=/Applications/Xcode-27.0.0.app/Contents/Developer
        '';
      };
    };
}
