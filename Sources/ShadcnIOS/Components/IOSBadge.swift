import SwiftUI

public enum IOSBadgeVariant: CaseIterable {
    case neutral, secondary, success, destructive
}

public struct IOSBadge: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let symbol: String?
    public let variant: IOSBadgeVariant

    public init(_ title: String, symbol: String? = nil, variant: IOSBadgeVariant = .neutral) {
        self.title = title
        self.symbol = symbol
        self.variant = variant
    }

    public var body: some View {
        let colors = theme.palette(for: scheme)
        HStack(spacing: theme.spacing.xxs) {
            if let symbol {
                Image(systemName: symbol).accessibilityHidden(true)
            }
            Text(title)
        }
        .font(.caption.weight(.semibold))
        .foregroundStyle(foreground(colors))
        .padding(.horizontal, theme.spacing.xs)
        .padding(.vertical, theme.spacing.xxs)
        .background(background(colors), in: RoundedRectangle(cornerRadius: theme.radii.badge))
        .accessibilityElement(children: .combine)
    }

    private func foreground(_ colors: IOSPalette) -> Color {
        switch variant {
        case .neutral: colors.primaryForeground
        case .secondary: colors.secondaryForeground
        case .success: colors.successForeground
        case .destructive: colors.destructiveForeground
        }
    }

    private func background(_ colors: IOSPalette) -> Color {
        switch variant {
        case .neutral: colors.primary
        case .secondary: colors.secondary
        case .success: colors.success
        case .destructive: colors.destructive
        }
    }
}
