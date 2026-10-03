// swift-tools-version: 6.3
import Foundation
import PackageDescription

let localMacroManifest = URL(fileURLWithPath: #filePath)
    .deletingLastPathComponent()
    .appendingPathComponent(".prepared/AppMacros/Package.swift")
let useLocalDependencies = ProcessInfo.processInfo.environment["SHADCN_IOS_LOCAL_DEPS"] == "1"
    && FileManager.default.fileExists(atPath: localMacroManifest.path)
let macroDependency: Package.Dependency = if useLocalDependencies {
    .package(name: "swift-app-macros", path: ".prepared/AppMacros")
} else {
    .package(url: "https://github.com/9uiLe/swift-app-macros.git", revision: "c87f52673499ab71bac7e841290a5fa4261a8a0a")
}

let package = Package(
    name: "ShadcnIOS",
    defaultLocalization: "en",
    platforms: [.iOS(.v26)],
    products: [.library(name: "ShadcnIOS", targets: ["ShadcnIOS"])],
    dependencies: [macroDependency],
    targets: [
        .target(name: "ShadcnIOS", dependencies: [.product(name: "AppMacros", package: "swift-app-macros")]),
        .testTarget(name: "ShadcnIOSTests", dependencies: ["ShadcnIOS"]),
    ]
)
