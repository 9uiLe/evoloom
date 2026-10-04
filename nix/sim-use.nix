{
  stdenvNoCC,
  fetchurl,
  lib,
}:

stdenvNoCC.mkDerivation {
  pname = "sim-use";
  version = "0.14.0";

  src = fetchurl {
    url = "https://github.com/lycorp-jp/sim-use/releases/download/v0.14.0/sim-use-v0.14.0.tar.gz";
    hash = "sha256-Z+LuKackYnLehkbkZmSpPZzrys4TQJTP09B9+4K9o+Y=";
  };
  licenseFile = fetchurl {
    url = "https://raw.githubusercontent.com/lycorp-jp/sim-use/v0.14.0/LICENSE";
    hash = "sha256-jA/iiSNENYtJqgfZoYS9jQiRgyuvZC8ZFh8nGswHXTI=";
  };

  sourceRoot = ".";
  dontBuild = true;
  dontStrip = true;

  installPhase = ''
    runHook preInstall
    mkdir -p "$out/bin"
    cp -p sim-use "$out/bin/sim-use"
    cp -R SimUse_SimUse.bundle SimUse_AndroidBackend.bundle "$out/bin/"
    mkdir -p "$out/share/licenses/sim-use"
    cp "$licenseFile" "$out/share/licenses/sim-use/LICENSE"
    runHook postInstall
  '';

  meta = {
    description = "Observe and operate iOS Simulator screens";
    homepage = "https://github.com/lycorp-jp/sim-use";
    platforms = [ "aarch64-darwin" ];
    license = lib.licenses.asl20;
    mainProgram = "sim-use";
  };
}
