import SwiftUI

public struct IOSEmptyState<Action: View>: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    public let title: String
    public let message: String
    public let symbol: String
    private let action: Action

    public init(
        _ title: String, message: String, symbol: String = "tray",
        @ViewBuilder action: () -> Action
    ) {
        self.title = title
        self.message = message
        self.symbol = symbol
        self.action = action()
    }

    public var body: some View {
        let colors = theme.palette(for: scheme)
        VStack(spacing: theme.spacing.sm) {
            Image(systemName: symbol)
                .font(.largeTitle)
                .foregroundStyle(colors.mutedForeground)
                .accessibilityHidden(true)
            Text(title).font(.headline)
            Text(message)
                .font(.subheadline)
                .foregroundStyle(colors.mutedForeground)
                .multilineTextAlignment(.center)
            action.padding(.top, theme.spacing.xxs)
        }
        .frame(maxWidth: .infinity)
        .padding(theme.spacing.lg)
    }
}

public extension IOSEmptyState where Action == EmptyView {
    init(_ title: String, message: String, symbol: String = "tray") {
        self.init(title, message: message, symbol: symbol) { EmptyView() }
    }
}
