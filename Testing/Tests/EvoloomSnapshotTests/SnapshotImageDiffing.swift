import SnapshotTesting
import UIKit

private struct PixelImage {
    let width: Int
    let height: Int
    let bytes: [UInt8]
}

func exactImageDiffing(_ imageDiffing: Diffing<UIImage>, root: URL, name: String) -> Diffing<UIImage> {
    Diffing<UIImage>(toData: imageDiffing.toData, fromData: imageDiffing.fromData) { expected, actual in
        let saveStarted = ProcessInfo.processInfo.systemUptime
        let rendered = root.appendingPathComponent("TestResults/Rendered")
        do {
            try FileManager.default.createDirectory(at: rendered, withIntermediateDirectories: true)
            guard let data = actual.pngData() else { throw CocoaError(.fileWriteUnknown) }
            try data.write(to: rendered.appendingPathComponent("components.\(name).png"))
            let seconds = ProcessInfo.processInfo.systemUptime - saveStarted
            try String(seconds).write(
                to: rendered.appendingPathComponent("components.\(name).seconds"),
                atomically: true, encoding: .utf8
            )
        } catch {
            return ("Could not save rendered image for \(name): \(error)", [])
        }
        guard let old = pixels(expected), let new = pixels(actual) else {
            return ("Image pixels could not be read", [])
        }
        guard old.width == new.width, old.height == new.height, old.bytes == new.bytes else {
            let directory = root.appendingPathComponent("TestResults/SnapshotDiffs/\(name)")
            try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
            try? expected.pngData()?.write(to: directory.appendingPathComponent("expected.png"))
            try? actual.pngData()?.write(to: directory.appendingPathComponent("actual.png"))
            if let image = difference(old: old, new: new) {
                try? image.pngData()?.write(to: directory.appendingPathComponent("diff.png"))
            }
            return ("Pixel difference for \(name). Inspect expected, actual and diff in \(directory.path)", [])
        }
        return nil
    }
}

private func pixels(_ image: UIImage) -> PixelImage? {
    guard let source = image.cgImage else { return nil }
    let width = source.width
    let height = source.height
    var bytes = [UInt8](repeating: 0, count: width * height * 4)
    let success = bytes.withUnsafeMutableBytes { buffer in
        guard let context = CGContext(
            data: buffer.baseAddress, width: width, height: height,
            bitsPerComponent: 8, bytesPerRow: width * 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return false }
        context.draw(source, in: CGRect(x: 0, y: 0, width: width, height: height))
        return true
    }
    return success ? PixelImage(width: width, height: height, bytes: bytes) : nil
}

private func difference(old: PixelImage, new: PixelImage) -> UIImage? {
    guard old.width == new.width, old.height == new.height else { return nil }
    var bytes = [UInt8](repeating: 255, count: old.bytes.count)
    for index in stride(from: 0, to: bytes.count, by: 4) {
        let changed = (0 ..< 4).contains { old.bytes[index + $0] != new.bytes[index + $0] }
        if changed {
            bytes[index] = 255
            bytes[index + 1] = 0
            bytes[index + 2] = 80
        }
    }
    guard let provider = CGDataProvider(data: Data(bytes) as CFData),
          let image = CGImage(
              width: old.width, height: old.height, bitsPerComponent: 8, bitsPerPixel: 32,
              bytesPerRow: old.width * 4, space: CGColorSpaceCreateDeviceRGB(),
              bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue),
              provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent
          ) else { return nil }
    return UIImage(cgImage: image)
}
