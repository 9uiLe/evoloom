// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "ShadcnIOS",
    defaultLocalization: "en",
    platforms: [.iOS(.v17)],
    products: [.library(name: "ShadcnIOS", targets: ["ShadcnIOS"])],
    targets: [
        .target(name: "ShadcnIOS"),
        .testTarget(name: "ShadcnIOSTests", dependencies: ["ShadcnIOS"]),
    ]
)
