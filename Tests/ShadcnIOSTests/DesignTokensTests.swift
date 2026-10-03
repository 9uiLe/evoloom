import ShadcnIOS
import SwiftUI
import XCTest

final class DesignTokensTests: XCTestCase {
    func testFoundationAndComponentTokens() {
        let tokens = IOSDesignTokens.neutral
        XCTAssertEqual(
            [tokens.spacing.xxs, tokens.spacing.xs, tokens.spacing.sm, tokens.spacing.md, tokens.spacing.lg, tokens.spacing.xl],
            [4, 8, 12, 16, 24, 32]
        )
        XCTAssertGreaterThan(tokens.radii.control, 0)
        XCTAssertGreaterThan(tokens.radii.card, tokens.radii.control)
        XCTAssertEqual(tokens.controls.minimumHeight, 44)
        XCTAssertEqual(tokens.controls.textAreaHeight, 110)
        XCTAssertEqual(tokens.controls.skeletonHeight, 20)
    }

    func testTokensAreCopyOnWriteValues() {
        var custom = IOSDesignTokens.neutral
        custom.spacing.md = 20
        custom.controls.minimumHeight = 48
        XCTAssertEqual(custom.spacing.md, 20)
        XCTAssertEqual(custom.controls.minimumHeight, 48)
        XCTAssertEqual(IOSDesignTokens.neutral.spacing.md, 16)
        XCTAssertEqual(IOSDesignTokens.neutral.controls.minimumHeight, 44)
    }

    @MainActor
    func testPrimaryContrastInBothSchemes() {
        for palette in [IOSDesignTokens.neutral.light, IOSDesignTokens.neutral.dark] {
            XCTAssertGreaterThanOrEqual(contrast(palette.primary, palette.primaryForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.background, palette.foreground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.card, palette.cardForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.secondary, palette.secondaryForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.muted, palette.mutedForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.destructive, palette.destructiveForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.muted, palette.destructiveText), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.success, palette.successForeground), 4.5)
            XCTAssertGreaterThanOrEqual(contrast(palette.background, palette.input), 3)
        }
        let dark = IOSDesignTokens.neutral.dark
        XCTAssertGreaterThanOrEqual(contrast(dark.toggleOnBackground, .white), 3)
        XCTAssertGreaterThanOrEqual(contrast(dark.toggleOnBackground, dark.background), 3)
    }

    @MainActor
    private func contrast(_ first: Color, _ second: Color) -> Double {
        func luminance(_ color: Color) -> Double {
            var red: CGFloat = 0
            var green: CGFloat = 0
            var blue: CGFloat = 0
            var alpha: CGFloat = 0
            XCTAssertTrue(UIColor(color).getRed(&red, green: &green, blue: &blue, alpha: &alpha))
            func linear(_ channel: CGFloat) -> Double {
                let value = Double(channel)
                return value <= 0.04045 ? value / 12.92 : pow((value + 0.055) / 1.055, 2.4)
            }
            return 0.2126 * linear(red) + 0.7152 * linear(green) + 0.0722 * linear(blue)
        }
        let values = [luminance(first), luminance(second)].sorted()
        return (values[1] + 0.05) / (values[0] + 0.05)
    }
}
