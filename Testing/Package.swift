// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "EvoloomVisualTests",
    platforms: [.iOS(.v26)],
    dependencies: [
        .package(name: "Evoloom", path: ".."),
        .package(name: "SnapshotTestingLocal", path: "../.prepared/SnapshotTesting"),
    ],
    targets: [
        .testTarget(
            name: "EvoloomSnapshotTests",
            dependencies: [
                .product(name: "Evoloom", package: "Evoloom"),
                .product(name: "SnapshotTesting", package: "SnapshotTestingLocal"),
            ]
        ),
    ]
)
