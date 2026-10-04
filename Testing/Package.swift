// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "EvoloomVisualTests",
    platforms: [.iOS(.v26)],
    products: [.library(name: "EvoloomReviewFixtures", targets: ["EvoloomReviewFixtures"])],
    dependencies: [
        .package(name: "Evoloom", path: ".."),
        .package(name: "SnapshotTestingLocal", path: "../.prepared/SnapshotTesting"),
    ],
    targets: [
        .target(
            name: "EvoloomReviewFixtures",
            dependencies: [.product(name: "Evoloom", package: "Evoloom")]
        ),
        .testTarget(
            name: "EvoloomSnapshotTests",
            dependencies: [
                .product(name: "Evoloom", package: "Evoloom"),
                "EvoloomReviewFixtures",
                .product(name: "SnapshotTesting", package: "SnapshotTestingLocal"),
            ]
        ),
    ]
)
