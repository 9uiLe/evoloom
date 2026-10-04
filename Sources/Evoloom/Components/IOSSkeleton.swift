import AppMacros
import SwiftUI

/// Static by design, so screenshots and Reduce Motion are stable.
@AutoEquatableView
public struct IOSSkeleton: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme
    public var height: CGFloat?

    public init(height: CGFloat? = nil) {
        self.height = height
    }

    public var equatableBody: some View {
        RoundedRectangle(cornerRadius: tokens.radii.badge)
            .fill(tokens.palette(for: scheme).muted)
            .frame(height: height ?? tokens.controls.skeletonHeight)
            .accessibilityHidden(true)
    }
}
