// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "Evoloom",
    defaultLocalization: "en",
    platforms: [.iOS(.v26)],
    products: [.library(name: "Evoloom", targets: ["Evoloom"])],
    targets: [
        .target(name: "Evoloom"),
        .testTarget(name: "EvoloomTests", dependencies: ["Evoloom"]),
    ]
)
