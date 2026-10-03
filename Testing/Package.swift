// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "ShadcnIOSVisualTests",
    platforms: [.iOS(.v26)],
    dependencies: [
        .package(name: "ShadcnIOS", path: ".."),
        .package(name: "SnapshotTestingLocal", path: "../.prepared/SnapshotTesting"),
    ],
    targets: [
        .testTarget(
            name: "ShadcnIOSSnapshotTests",
            dependencies: [
                .product(name: "ShadcnIOS", package: "ShadcnIOS"),
                .product(name: "SnapshotTesting", package: "SnapshotTestingLocal"),
            ]
        ),
    ]
)
