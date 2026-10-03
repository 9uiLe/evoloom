import SwiftUI

public struct IOSSwitch: View {
    @Environment(\.iosTheme) private var theme
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
            VStack(alignment: .leading, spacing: theme.spacing.xxs) {
                Text(title)
                if let detail {
                    Text(detail)
                        .font(.footnote)
                        .foregroundStyle(theme.palette(for: scheme).mutedForeground)
                }
            }
        }
        .tint(theme.palette(for: scheme).primary)
    }
}
