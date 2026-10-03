import SwiftUI

/// Static by design, so screenshots and Reduce Motion are stable.
public struct IOSSkeleton: View {
    @Environment(\.iosTheme) private var theme
    @Environment(\.colorScheme) private var scheme
    public var height: CGFloat

    public init(height: CGFloat = 20) {
        self.height = height
    }

    public var body: some View {
        RoundedRectangle(cornerRadius: theme.radii.badge)
            .fill(theme.palette(for: scheme).muted)
            .frame(height: height)
            .accessibilityHidden(true)
    }
}
