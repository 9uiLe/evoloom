import SwiftUI

public struct IOSCard<Content: View>: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    private let content: Content

    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    public var body: some View {
        content
            .padding(theme.spacing.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(theme.palette(for: scheme).card, in: RoundedRectangle(cornerRadius: theme.radii.card))
            .overlay {
                RoundedRectangle(cornerRadius: theme.radii.card)
                    .strokeBorder(theme.palette(for: scheme).border)
            }
    }
}

public struct IOSCardHeader: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let detail: String?

    public init(_ title: String, detail: String? = nil) {
        self.title = title
        self.detail = detail
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: theme.spacing.xxs) {
            Text(title).font(.headline)
            if let detail {
                Text(detail)
                    .font(.subheadline)
                    .foregroundStyle(theme.palette(for: scheme).mutedForeground)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
