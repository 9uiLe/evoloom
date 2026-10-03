import SwiftUI

public enum IOSAlertVariant {
    case information, error
}

public struct IOSInlineAlert: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let message: String
    public let variant: IOSAlertVariant

    public init(_ title: String, message: String, variant: IOSAlertVariant = .information) {
        self.title = title
        self.message = message
        self.variant = variant
    }

    public var body: some View {
        let colors = theme.palette(for: scheme)
        HStack(alignment: .top, spacing: theme.spacing.sm) {
            Image(systemName: variant == .error ? "exclamationmark.triangle" : "info.circle")
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: theme.spacing.xxs) {
                Text(title).font(.subheadline.weight(.semibold))
                Text(message).font(.subheadline)
            }
            Spacer(minLength: 0)
        }
        .foregroundStyle(variant == .error ? colors.destructiveText : colors.foreground)
        .padding(theme.spacing.md)
        .background(colors.muted, in: RoundedRectangle(cornerRadius: theme.radii.control))
        .accessibilityElement(children: .combine)
    }
}
