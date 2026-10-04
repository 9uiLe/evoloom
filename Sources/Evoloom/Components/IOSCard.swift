import AppMacros
import SwiftUI

@AutoEquatableView
public struct IOSCard<Content: View>: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    @SkipEquatable private let content: Content

    public init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    public var equatableBody: some View {
        content
            .padding(tokens.spacing.md)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(tokens.palette(for: scheme).card, in: RoundedRectangle(cornerRadius: tokens.radii.card))
            .overlay {
                RoundedRectangle(cornerRadius: tokens.radii.card)
                    .strokeBorder(tokens.palette(for: scheme).border, lineWidth: tokens.controls.borderWidth)
            }
    }
}

@AutoEquatableView
public struct IOSCardHeader: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let detail: String?

    public init(_ title: String, detail: String? = nil) {
        self.title = title
        self.detail = detail
    }

    public var equatableBody: some View {
        VStack(alignment: .leading, spacing: tokens.spacing.xxs) {
            Text(title).font(tokens.typography.cardTitle)
            if let detail {
                Text(detail)
                    .font(tokens.typography.cardDetail)
                    .foregroundStyle(tokens.palette(for: scheme).mutedForeground)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
