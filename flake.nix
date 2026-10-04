{
  description = "Evoloom development tools and fixed test source";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/44a91898084f46797b5fac650c7e8c9ac38c43d4";
    snapshot = {
      url = "github:pointfreeco/swift-snapshot-testing/1.18.9";
      flake = false;
    };
  };
  outputs =
    {
      nixpkgs,
      snapshot,
      ...
    }:
    let
      systems = [
        "aarch64-darwin"
        "x86_64-linux"
      ];
    in
    {
      devShells = nixpkgs.lib.genAttrs systems (
        system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              swiftlint
              swiftformat
              just
              python3
              ruff
              nixfmt
              yamllint
              actionlint
              shellcheck
              shfmt
            ];
            SNAPSHOT_SOURCE = "${snapshot}";
            shellHook = nixpkgs.lib.optionalString (system == "aarch64-darwin") ''
              unset SDKROOT
              export DEVELOPER_DIR="''${EVOLOOM_XCODE_DEVELOPER_DIR:-/Applications/Xcode-27.0.0.app/Contents/Developer}"
            '';
          };
        }
      );
    };
}
