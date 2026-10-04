import AppMacros
import SwiftUI

public enum IOSButtonVariant: CaseIterable {
    case primary, secondary, outline, ghost, destructive
}

public enum IOSButtonSize {
    case compact, regular, large

    func horizontalPadding(_ spacing: IOSSpacingTokens) -> CGFloat {
        switch self {
        case .compact: spacing.sm
        case .regular: spacing.md
        case .large: spacing.lg
        }
    }
}

/// A reusable style for native Button, including Button(role: .destructive).
public struct IOSButtonStyle: ButtonStyle {
    @Environment(\.iosDesignTokens) private var tokens
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
        let colors = tokens.palette(for: scheme)
        let effective = configuration.role == .destructive ? IOSButtonVariant.destructive : variant
        configuration.label
            .font(tokens.typography.button)
            .foregroundStyle(isEnabled ? foreground(effective, colors: colors) : colors.mutedForeground)
            .padding(.vertical, tokens.spacing.xs)
            .frame(minHeight: tokens.controls.minimumHeight)
            .padding(.horizontal, size.horizontalPadding(tokens.spacing))
            .background(isEnabled ? background(effective, colors: colors) : colors.muted, in: RoundedRectangle(cornerRadius: tokens.radii.control))
            .overlay {
                RoundedRectangle(cornerRadius: tokens.radii.control)
                    .strokeBorder(
                        effective == .outline ? colors.border : .clear,
                        lineWidth: contrast == .increased ? tokens.controls.emphasizedBorderWidth : tokens.controls.borderWidth
                    )
            }
            .opacity(configuration.isPressed ? tokens.controls.pressedOpacity : 1)
            .contentShape(Rectangle())
    }

    private func foreground(_ variant: IOSButtonVariant, colors: IOSColorTokens) -> Color {
        switch variant {
        case .primary: colors.primaryForeground
        case .secondary: colors.secondaryForeground
        case .outline, .ghost: colors.foreground
        case .destructive: colors.destructiveForeground
        }
    }

    private func background(_ variant: IOSButtonVariant, colors: IOSColorTokens) -> Color {
        switch variant {
        case .primary: colors.primary
        case .secondary: colors.secondary
        case .outline, .ghost: .clear
        case .destructive: colors.destructive
        }
    }
}

@AutoEquatableView
public struct IOSButton<Label: View>: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.isEnabled) private var isEnabled
    private let variant: IOSButtonVariant
    private let size: IOSButtonSize
    private let isLoading: Bool
    private let action: () -> Void
    @SkipEquatable private let label: Label

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

    public var equatableBody: some View {
        Button(action: { trigger(isEnabled: isEnabled) }, label: {
            HStack(spacing: tokens.spacing.xs) {
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
