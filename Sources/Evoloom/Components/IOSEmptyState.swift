import AppMacros
import SwiftUI

@AutoEquatableView
public struct IOSEmptyState<Action: View>: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let message: String
    public let symbol: String
    @SkipEquatable private let action: Action

    public init(
        _ title: String, message: String, symbol: String = "tray",
        @ViewBuilder action: () -> Action
    ) {
        self.title = title
        self.message = message
        self.symbol = symbol
        self.action = action()
    }

    @ViewBuilder public var equatableBody: some View {
        let colors = tokens.palette(for: scheme)
        VStack(spacing: tokens.spacing.sm) {
            Image(systemName: symbol)
                .font(tokens.typography.emptyIcon)
                .foregroundStyle(colors.mutedForeground)
                .accessibilityHidden(true)
            Text(title)
                .font(tokens.typography.emptyTitle)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            Text(message)
                .font(tokens.typography.emptyMessage)
                .foregroundStyle(colors.mutedForeground)
                .multilineTextAlignment(.center)
                .fixedSize(horizontal: false, vertical: true)
            action.padding(.top, tokens.spacing.xxs)
        }
        .frame(maxWidth: .infinity)
        .padding(tokens.spacing.lg)
    }
}

public extension IOSEmptyState where Action == EmptyView {
    init(_ title: String, message: String, symbol: String = "tray") {
        self.init(title, message: message, symbol: symbol) { EmptyView() }
    }
}
