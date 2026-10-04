// swift-tools-version: 6.3
import Foundation
import PackageDescription

let localMacroManifest = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent()
    .appendingPathComponent(".prepared/AppMacros/Package.swift")
let useLocalDependencies = ProcessInfo.processInfo.environment["EVOLOOM_LOCAL_DEPS"] == "1"
    && FileManager.default.fileExists(atPath: localMacroManifest.path)
let macroDependency: Package.Dependency = if useLocalDependencies {
    .package(name: "swift-app-macros", path: ".prepared/AppMacros")
} else {
    .package(url: "https://github.com/9uiLe/swift-app-macros.git", revision: "4146637f4d9cf59e5051840311063ddd45a1b316")
}

let package = Package(
    name: "Evoloom",
    defaultLocalization: "en",
    platforms: [.iOS(.v26)],
    products: [.library(name: "Evoloom", targets: ["Evoloom"])],
    dependencies: [macroDependency],
    targets: [
        .target(name: "Evoloom", dependencies: [.product(name: "AppMacros", package: "swift-app-macros")]),
        .testTarget(name: "EvoloomTests", dependencies: ["Evoloom"]),
    ]
)
