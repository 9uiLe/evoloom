import SwiftUI

public struct IOSSeparator: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme

    public init() {}

    public var body: some View {
        Rectangle()
            .fill(theme.palette(for: scheme).border)
            .frame(height: 1)
            .accessibilityHidden(true)
    }
}
