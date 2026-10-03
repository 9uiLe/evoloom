import SwiftUI

public struct IOSSwitch: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @Binding var isOn: Bool
    public let title: String
    public let detail: String?

    public init(_ title: String, isOn: Binding<Bool>, detail: String? = nil) {
        self.title = title
        _isOn = isOn
        self.detail = detail
    }

    public var body: some View {
        Toggle(isOn: $isOn) {
            VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
                Text(title)
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
