import AppMacros
import SwiftUI

@AutoEquatableView
public struct IOSSeparator: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme

    public init() {}

    public var equatableBody: some View {
        Rectangle()
            .fill(tokens.palette(for: scheme).border)
            .frame(height: tokens.controls.separatorThickness)
            .accessibilityHidden(true)
    }
}
