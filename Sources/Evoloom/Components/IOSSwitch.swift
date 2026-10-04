import AppMacros
import SwiftUI

@AutoEquatableView
public struct IOSSwitch: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @Environment(\.accessibilityDifferentiateWithoutColor) private var differentiateWithoutColor
    @Binding var isOn: Bool
    public let title: String
    public let detail: String?
    private let onStateLabel: LocalizedStringKey
    private let offStateLabel: LocalizedStringKey

    public init(
        _ title: String, isOn: Binding<Bool>, detail: String? = nil,
        onStateLabel: LocalizedStringKey = "On", offStateLabel: LocalizedStringKey = "Off"
    ) {
        self.title = title
        _isOn = isOn
        self.detail = detail
        self.onStateLabel = onStateLabel
        self.offStateLabel = offStateLabel
    }

    public var equatableBody: some View {
        Toggle(isOn: $isOn) {
            VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
                Text(title)
                if scheme == .dark || differentiateWithoutColor {
                    HStack(spacing: tokens.spacing.xxs) {
                        Image(systemName: isOn ? "checkmark.circle.fill" : "circle")
                        Text(isOn ? onStateLabel : offStateLabel)
                    }
                    .font(tokens.typography.supporting.weight(.semibold))
                    .foregroundStyle(isOn ? tokens.palette(for: scheme).foreground : tokens.palette(for: scheme).mutedForeground)
                    .accessibilityHidden(true)
                }
                if let detail {
                    Text(detail)
                        .font(tokens.typography.supporting)
                        .foregroundStyle(tokens.palette(for: scheme).mutedForeground)
                }
            }
        }
        .tint(tokens.palette(for: scheme).toggleOnBackground)
    }
}
