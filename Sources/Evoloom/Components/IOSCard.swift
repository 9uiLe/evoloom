import SwiftUI

/// A token-styled surface for related content. Explicit child foreground styles remain in control.
public struct IOSCard<Content: View>: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    private let content: Content

    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    public var body: some View {
        content
            .foregroundStyle(tokens.palette(for: scheme).cardForeground)
            .padding(tokens.spacing.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(tokens.palette(for: scheme).card, in: RoundedRectangle(cornerRadius: tokens.radii.card))
            .overlay {
                RoundedRectangle(cornerRadius: tokens.radii.card)
                    .strokeBorder(tokens.palette(for: scheme).border, lineWidth: tokens.controls.borderWidth)
            }
    }
}

public struct IOSCardHeader: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let detail: String?

    public init(_ title: String, detail: String? = nil) {
        self.title = title
        self.detail = detail
    }

    public var body: some View {
        VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
            Text(title)
                .font(tokens.typography.cardTitle)
                .foregroundStyle(tokens.palette(for: scheme).cardForeground)
            if let detail {
                Text(detail)
                    .font(tokens.typography.cardDetail)
                    .foregroundStyle(tokens.palette(for: scheme).cardMutedForeground)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
