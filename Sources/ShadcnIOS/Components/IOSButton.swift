import SwiftUI

public enum IOSButtonVariant: CaseIterable {
    case primary, secondary, outline, ghost, destructive
}

public enum IOSButtonSize {
    case compact, regular, large

    var horizontalPadding: CGFloat {
        switch self {
        case .compact: 12
        case .regular: 16
        case .large: 24
        }
    }
}

/// A reusable style for native Button, including Button(role: .destructive).
public struct IOSButtonStyle: ButtonStyle {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    @Environment(\.colorSchemeContrast) private var contrast
    @Environment(\.isEnabled) private var isEnabled

    public var variant: IOSButtonVariant
    public var size: IOSButtonSize

    public init(_ variant: IOSButtonVariant = .primary, size: IOSButtonSize = .regular) {
        self.variant = variant
        self.size = size
    }

    public func makeBody(configuration: Configuration) -> some View {
        let colors = theme.palette(for: scheme)
        let effective = configuration.role == .destructive ? IOSButtonVariant.destructive : variant
        configuration.label
            .font(.body.weight(.semibold))
            .foregroundStyle(isEnabled ? foreground(effective, colors: colors) : colors.mutedForeground)
            .padding(.vertical, theme.spacing.xs)
            .frame(minHeight: 44)
            .padding(.horizontal, size.horizontalPadding)
            .background(isEnabled ? background(effective, colors: colors) : colors.muted, in: RoundedRectangle(cornerRadius: theme.radii.control))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radii.control)
                    .strokeBorder(effective == .outline ? colors.border : .clear, lineWidth: contrast == .increased ? 2 : 1)
            }
            .opacity(configuration.isPressed ? 0.75 : 1)
            .contentShape(Rectangle())
    }

    private func foreground(_ variant: IOSButtonVariant, colors: IOSPalette) -> Color {
        switch variant {
        case .primary: colors.primaryForeground
        case .secondary: colors.secondaryForeground
        case .outline, .ghost: colors.foreground
        case .destructive: colors.destructiveForeground
        }
    }

    private func background(_ variant: IOSButtonVariant, colors: IOSPalette) -> Color {
        switch variant {
        case .primary: colors.primary
        case .secondary: colors.secondary
        case .outline, .ghost: .clear
        case .destructive: colors.destructive
        }
    }
}

public struct IOSButton<Label: View>: View {
    @Environment(\.isEnabled) private var isEnabled
    private let variant: IOSButtonVariant
    private let size: IOSButtonSize
    private let isLoading: Bool
    private let action: () -> Void
    private let label: Label

    public init(
        variant: IOSButtonVariant = .primary,
        size: IOSButtonSize = .regular,
        isLoading: Bool = false,
        action: @escaping () -> Void,
        @ViewBuilder label: () -> Label
    ) {
        self.variant = variant
        self.size = size
        self.isLoading = isLoading
        self.action = action
        self.label = label()
    }

    public var body: some View {
        Button(action: { trigger(isEnabled: isEnabled) }, label: {
            HStack(spacing: 8) {
                if isLoading {
                    Image(systemName: "hourglass")
                        .accessibilityHidden(true)
                }
                label
            }
        })
        .buttonStyle(IOSButtonStyle(variant, size: size))
        .disabled(isLoading)
        .accessibilityHint(isLoading ? "Loading" : "")
    }

    func trigger(isEnabled: Bool) {
        guard isEnabled, !isLoading else { return }
        action()
    }
}

public extension IOSButton where Label == Text {
    init(
        _ title: String,
        variant: IOSButtonVariant = .primary,
        size: IOSButtonSize = .regular,
        isLoading: Bool = false,
        action: @escaping () -> Void
    ) {
        self.init(variant: variant, size: size, isLoading: isLoading, action: action) {
            Text(title)
        }
    }
}
