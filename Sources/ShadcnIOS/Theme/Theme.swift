import SwiftUI

/// Semantic colors are paired so callers do not need to invent contrast relationships.
public struct IOSPalette: Sendable {
    public var background: Color
    public var foreground: Color
    public var card: Color
    public var cardForeground: Color
    public var primary: Color
    public var primaryForeground: Color
    public var secondary: Color
    public var secondaryForeground: Color
    public var muted: Color
    public var mutedForeground: Color
    public var border: Color
    public var input: Color
    public var destructive: Color
    public var destructiveForeground: Color
    public var destructiveText: Color
    public var success: Color
    public var successForeground: Color

    public init(
        background: Color, foreground: Color, card: Color, cardForeground: Color,
        primary: Color, primaryForeground: Color, secondary: Color,
        secondaryForeground: Color, muted: Color, mutedForeground: Color,
        border: Color, input: Color, destructive: Color, destructiveForeground: Color,
        destructiveText: Color, success: Color, successForeground: Color
    ) {
        self.background = background
        self.foreground = foreground
        self.card = card
        self.cardForeground = cardForeground
        self.primary = primary
        self.primaryForeground = primaryForeground
        self.secondary = secondary
        self.secondaryForeground = secondaryForeground
        self.muted = muted
        self.mutedForeground = mutedForeground
        self.border = border
        self.input = input
        self.destructive = destructive
        self.destructiveForeground = destructiveForeground
        self.destructiveText = destructiveText
        self.success = success
        self.successForeground = successForeground
    }
}

public struct IOSSpacing: Sendable {
    public var xxs: CGFloat = 4
    public var xs: CGFloat = 8
    public var sm: CGFloat = 12
    public var md: CGFloat = 16
    public var lg: CGFloat = 24
    public var xl: CGFloat = 32

    public init() {}
}

public struct IOSRadii: Sendable {
    public var control: CGFloat = 10
    public var card: CGFloat = 14
    public var badge: CGFloat = 6

    public init() {}
}

public struct IOSTheme: Sendable {
    public var light: IOSPalette
    public var dark: IOSPalette
    public var spacing: IOSSpacing
    public var radii: IOSRadii

    public init(light: IOSPalette, dark: IOSPalette, spacing: IOSSpacing = .init(), radii: IOSRadii = .init()) {
        self.light = light
        self.dark = dark
        self.spacing = spacing
        self.radii = radii
    }

    public static let neutral = IOSTheme(
        light: IOSPalette(
            background: Color(red: 1, green: 1, blue: 1), foreground: Color(red: 0.09, green: 0.09, blue: 0.11),
            card: .white, cardForeground: Color(red: 0.09, green: 0.09, blue: 0.11),
            primary: Color(red: 0.09, green: 0.09, blue: 0.11), primaryForeground: .white,
            secondary: Color(red: 0.96, green: 0.96, blue: 0.97), secondaryForeground: Color(red: 0.09, green: 0.09, blue: 0.11),
            muted: Color(red: 0.96, green: 0.96, blue: 0.97), mutedForeground: Color(red: 0.38, green: 0.38, blue: 0.42),
            border: Color(red: 0.87, green: 0.87, blue: 0.89), input: Color(red: 0.54, green: 0.54, blue: 0.56),
            destructive: Color(red: 0.72, green: 0.10, blue: 0.13), destructiveForeground: .white,
            destructiveText: Color(red: 0.65, green: 0.08, blue: 0.10),
            success: Color(red: 0.80, green: 0.94, blue: 0.83), successForeground: Color(red: 0.05, green: 0.38, blue: 0.22)
        ),
        dark: IOSPalette(
            background: Color(red: 0.06, green: 0.06, blue: 0.07), foreground: Color(red: 0.98, green: 0.98, blue: 0.98),
            card: Color(red: 0.10, green: 0.10, blue: 0.12), cardForeground: Color(red: 0.98, green: 0.98, blue: 0.98),
            primary: Color(red: 0.98, green: 0.98, blue: 0.98), primaryForeground: Color(red: 0.09, green: 0.09, blue: 0.11),
            secondary: Color(red: 0.17, green: 0.17, blue: 0.19), secondaryForeground: Color(red: 0.98, green: 0.98, blue: 0.98),
            muted: Color(red: 0.17, green: 0.17, blue: 0.19), mutedForeground: Color(red: 0.68, green: 0.68, blue: 0.71),
            border: Color(red: 0.29, green: 0.29, blue: 0.32), input: Color(red: 0.54, green: 0.54, blue: 0.56),
            destructive: Color(red: 0.65, green: 0.16, blue: 0.16), destructiveForeground: .white,
            destructiveText: Color(red: 1, green: 0.70, blue: 0.70),
            success: Color(red: 0.08, green: 0.24, blue: 0.17), successForeground: Color(red: 0.68, green: 0.95, blue: 0.76)
        )
    )
}

public extension EnvironmentValues {
    @Entry var iosTheme: IOSTheme = .neutral
}

public extension View {
    func iosTheme(_ theme: IOSTheme) -> some View {
        environment(\.iosTheme, theme)
    }
}

extension IOSTheme {
    func palette(for scheme: ColorScheme) -> IOSPalette {
        scheme == .dark ? dark : light
    }
}
