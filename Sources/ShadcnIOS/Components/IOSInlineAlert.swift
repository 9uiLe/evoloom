import SwiftUI

public enum IOSAlertVariant {
    case information, error
}

public struct IOSInlineAlert: View {
    @Environment(\.iosDesignTokens) private var tokens
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
        let colors = tokens.palette(for: scheme)
        HStack(alignment: .top, spacing: tokens.spacing.sm) {
            Image(systemName: variant == .error ? "exclamationmark.triangle" : "info.circle")
                .accessibilityHidden(true)
            VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
                Text(title).font(tokens.typography.alertTitle)
                Text(message).font(tokens.typography.alertMessage)
            }
            Spacer(minLength: 0)
        }
        .foregroundStyle(variant == .error ? colors.destructiveText : colors.foreground)
        .padding(tokens.spacing.md)
        .background(colors.muted, in: RoundedRectangle(cornerRadius: tokens.radii.control))
        .accessibilityElement(children: .combine)
    }
}
