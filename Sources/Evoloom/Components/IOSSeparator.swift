import SwiftUI

public struct IOSSeparator: View {
    @Environment(\.iosDesignTokens) private var tokens
    @Environment(\.colorScheme) private var scheme

    public init() {}

    public var body: some View {
        Rectangle()
            .fill(tokens.palette(for: scheme).border)
            .frame(height: tokens.controls.separatorThickness)
            .accessibilityHidden(true)
    }
}
